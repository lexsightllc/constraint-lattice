# SPDX-License-Identifier: MPL-2.0
"""Simplified constraint lattice implementation used for tests.

This module defines a small :class:`ConstraintLattice` class capable of storing
nodes, registering constraint functions and propagating values until a stable
state is reached.  It is intentionally lightweight and independent from the
larger project to keep unit tests self contained.
"""
from __future__ import annotations

from collections import defaultdict
from numbers import Number
from typing import Any, Callable, Dict, Iterable, List, Sequence, Set, Tuple
import logging


logger = logging.getLogger(__name__)


class ConstraintLattice:
    """Minimal constraint lattice for propagating values between nodes."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Any] = {}
        self.constraints: List[Dict[str, Any]] = []

    def add_node(self, node_id: str, value: Any | None = None) -> None:
        """Add a node to the lattice."""
        self.nodes[node_id] = value

    def add_constraint(
        self,
        constraint_func: Callable[..., Any],
        *,
        inputs: Sequence[str],
        outputs: Sequence[str],
    ) -> None:
        """Register a new constraint function."""
        self.constraints.append({
            "func": constraint_func,
            "inputs": list(inputs),
            "outputs": list(outputs),
        })

    # ------------------------------------------------------------------
    # Propagation logic
    # ------------------------------------------------------------------
    def propagate(self) -> None:
        """Propagate all constraints until a fixed point is reached."""
        dep_graph: Dict[str, Set[int]] = defaultdict(set)
        for idx, constraint in enumerate(self.constraints):
            for input_id in constraint["inputs"]:
                dep_graph[input_id].add(idx)

        constraint_graph: Dict[int, Set[int]] = defaultdict(set)
        for idx, constraint in enumerate(self.constraints):
            for output_id in constraint["outputs"]:
                for dependent_idx in dep_graph.get(output_id, set()):
                    constraint_graph[idx].add(dependent_idx)

        sccs = list(reversed(self._tarjan_scc(constraint_graph)))
        logger.debug("found %d SCCs", len(sccs))

        tolerance = 1e-6
        iteration_limit = 1000

        for i, scc in enumerate(sccs):
            logger.debug("processing SCC %d: %s", i, scc)
            variables = sorted(
                {
                    node
                    for constraint_idx in scc
                    for node in self.constraints[constraint_idx]["outputs"]
                    if node in self.nodes
                }
            )
            var_index = {node: pos for pos, node in enumerate(variables)}

            solved = False
            rows: List[List[float]] = []
            constants: List[float] = []
            if var_index:
                for constraint_idx in scc:
                    constraint = self.constraints[constraint_idx]
                    inputs = constraint["inputs"]
                    outputs = constraint["outputs"]
                    baseline_inputs = [
                        float(self.nodes.get(node, 0.0)) for node in inputs
                    ]
                    base_output = constraint["func"](*baseline_inputs)
                    if not isinstance(base_output, tuple):
                        base_output = (base_output,)

                    for out_pos, output_id in enumerate(outputs):
                        if output_id not in var_index:
                            continue
                        row = [0.0] * len(var_index)
                        row[var_index[output_id]] = 1.0
                        constant = float(base_output[out_pos])

                        for inp_idx, input_id in enumerate(inputs):
                            if input_id not in var_index:
                                continue
                            perturbed = baseline_inputs.copy()
                            perturbed[inp_idx] += 1.0
                            perturbed_output = constraint["func"](*perturbed)
                            if not isinstance(perturbed_output, tuple):
                                perturbed_output = (perturbed_output,)
                            delta = float(
                                perturbed_output[out_pos] - base_output[out_pos]
                            )
                            row[var_index[input_id]] -= delta
                            constant -= delta * baseline_inputs[inp_idx]

                        rows.append(row)
                        constants.append(constant)

                if rows:
                    import numpy as np

                    A = np.array(rows, dtype=float)
                    b = np.array(constants, dtype=float)
                    try:
                        if np.linalg.matrix_rank(A) == len(var_index):
                            solution, *_ = np.linalg.lstsq(A, b, rcond=None)
                            for node, idx in var_index.items():
                                self.nodes[node] = float(round(solution[idx], 6))
                            solved = True
                        else:
                            solved = False
                    except np.linalg.LinAlgError:
                        solved = False

            if solved:
                continue

            seen_states: Set[Tuple[Tuple[str, Any], ...]] = set()
            iteration = 0
            while True:
                state_key = tuple(sorted(self.nodes.items()))
                if state_key in seen_states:
                    logger.debug("  detected repeating state; breaking")
                    break
                seen_states.add(state_key)

                iteration += 1
                if iteration > iteration_limit:
                    logger.debug("  iteration limit reached; breaking")
                    break
                changed = False
                logger.debug("  iteration %d", iteration)
                for constraint_idx in scc:
                    constraint = self.constraints[constraint_idx]
                    input_vals = [self.nodes[i] for i in constraint["inputs"]]
                    output_vals = constraint["func"](*input_vals)
                    if not isinstance(output_vals, tuple):
                        output_vals = (output_vals,)
                    for j, output_id in enumerate(constraint["outputs"]):
                        old_val = self.nodes.get(output_id)
                        new_val = output_vals[j]

                        if old_val is None or not isinstance(old_val, Number):
                            if old_val != new_val:
                                logger.debug(
                                    "    updating %s from %r to %r", output_id, old_val, new_val
                                )
                                self.nodes[output_id] = new_val
                                changed = True
                            continue

                        if isinstance(new_val, Number):
                            updated_val = old_val + 0.5 * (new_val - old_val)
                            if abs(updated_val - old_val) <= tolerance:
                                continue
                        else:
                            updated_val = new_val

                        if updated_val != old_val:
                            logger.debug(
                                "    updating %s from %r to %r", output_id, old_val, updated_val
                            )
                            self.nodes[output_id] = updated_val
                            changed = True

                if not changed:
                    break

            for node_id, value in list(self.nodes.items()):
                if isinstance(value, Number):
                    self.nodes[node_id] = float(round(value, 6))

    # ------------------------------------------------------------------
    # Tarjan strongly connected components
    # ------------------------------------------------------------------
    def _tarjan_scc(self, graph: Dict[int, Set[int]]) -> List[List[int]]:
        index = 0
        stack: List[int] = []
        indices: Dict[int, int] = {}
        lowlinks: Dict[int, int] = {}
        on_stack: Dict[int, bool] = {}
        sccs: List[List[int]] = []

        def strongconnect(node: int) -> None:
            nonlocal index
            indices[node] = index
            lowlinks[node] = index
            index += 1
            stack.append(node)
            on_stack[node] = True

            for neighbor in graph.get(node, set()):
                if neighbor not in indices:
                    strongconnect(neighbor)
                    lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
                elif on_stack.get(neighbor):
                    lowlinks[node] = min(lowlinks[node], indices[neighbor])

            if lowlinks[node] == indices[node]:
                scc: List[int] = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.append(w)
                    if w == node:
                        break
                sccs.append(scc)

        for node in graph:
            if node not in indices:
                strongconnect(node)

        return sccs
