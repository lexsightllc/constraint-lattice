# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 ochoaughini. All rights reserved.
# See LICENSE for full terms.

import importlib
import json
import os
import hashlib
import inspect
import re
from functools import partial
from typing import Any, List, Tuple, Type

import yaml  # type: ignore

from .schema import ConstraintConfig, ConstraintSchema
from constraint_lattice.engine import Constraint


def load_constraint_class(class_name: str) -> Type[Constraint]:
    """
    Load a constraint class by name.

    Args:
        class_name: Fully qualified name of the constraint class.

    Returns:
        The constraint class.

    Raises:
        ImportError: If the class cannot be found.
    """
    try:
        if "." not in class_name:
            module_name = "constraint_lattice.constraints"
        else:
            module_name, class_name = class_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except (ImportError, AttributeError, ValueError) as e:
        raise ImportError(f"Could not load constraint class {class_name}: {e}")


def _normalise_params(params: dict | None) -> Tuple[Tuple[Any, ...], dict[str, Any]]:
    """Split raw parameter mapping into positional and keyword components."""

    if not params:
        return (), {}

    param_copy: dict[str, Any] = dict(params)
    args = param_copy.pop("args", ())
    kwargs = param_copy.pop("kwargs", {})

    if not isinstance(args, (list, tuple)):
        raise TypeError("'args' parameter must be a list or tuple")
    if not isinstance(kwargs, dict):
        raise TypeError("'kwargs' parameter must be a mapping")

    kw = dict(kwargs)
    kw.update(param_copy)
    return tuple(args), kw


def _wrap_for_engine(candidate: Any, engine_hint: str | None) -> Any:
    """Apply engine specific wrappers (currently only JAX)."""

    if engine_hint != "jax":
        return candidate

    if isinstance(candidate, Constraint) or not callable(candidate):
        return candidate

    try:
        from engine.jax_backend import JAXConstraint  # Local import keeps optional dep lazy
    except Exception:  # pragma: no cover - optional dependency may be absent
        return candidate

    try:
        return JAXConstraint(candidate)
    except Exception:  # pragma: no cover - fall back to raw callable on failure
        return candidate


def _instantiate_constraint(
    target: Any, params: dict | None, engine_hint: str | None
) -> Constraint | Any:
    """Create a constraint instance or callable from YAML metadata."""

    args, kwargs = _normalise_params(params)

    if inspect.isclass(target):
        return target(*args, **kwargs)

    if callable(target):
        callable_target = target
        if args or kwargs:
            callable_target = partial(callable_target, *args, **kwargs)
        return _wrap_for_engine(callable_target, engine_hint)

    return target


def load_constraints_from_yaml(
    yaml_path: str,
    profile: str = "default",
    search_modules: List[str] | None = None,
) -> List[Constraint]:
    """
    Load constraints from a YAML configuration file.

    Args:
        yaml_path: Path to the YAML file.
        profile: Name of the profile to load.

    Returns:
        List of constraint instances.
    """
    config = _load_yaml(yaml_path)

    if profile not in config["profiles"]:
        raise ValueError(f"Profile '{profile}' not found in configuration")

    raw_entries = config["profiles"][profile]
    constraints = []
    search_modules = search_modules or []

    for entry in raw_entries:
        if isinstance(entry, str):
            class_name = entry
            params = {}
            engine_hint = None
        elif isinstance(entry, dict):
            class_name = entry["class"]
            params = entry.get("params", {})
            engine_hint = entry.get("engine")
        else:
            raise ValueError(f"Invalid entry type in profile: {type(entry)}")

        try:
            constraint_cls = load_constraint_class(class_name)
        except ImportError:
            constraint_cls = None
            if "." not in class_name:
                for module in search_modules:
                    try:
                        constraint_cls = load_constraint_class(
                            f"{module}.{class_name}"
                        )
                        break
                    except ImportError:
                        continue
            if constraint_cls is None:
                raise
        constraint = _instantiate_constraint(constraint_cls, params, engine_hint)
        constraints.append(constraint)

    return constraints


_YAML_ESCAPE_FIXER = re.compile(r"\\([^0abtnevfr\"\\/N_LPuxU])")


def _load_yaml(path: str) -> Any:
    with open(path, "r") as fh:
        raw = fh.read()

    if not raw:
        return {}

    def _escape(match: re.Match[str]) -> str:
        return "\\\\" + match.group(1)

    sanitized = _YAML_ESCAPE_FIXER.sub(_escape, raw)
    return yaml.safe_load(sanitized)


def load_constraints_from_file(path: str) -> List[ConstraintSchema]:
    """
    Load constraints from a YAML or JSON file

    Args:
        path: Path to constraint configuration file

    Returns:
        List of validated ConstraintSchema objects
    """
    # Read file
    if path.endswith((".yaml", ".yml")):
        config_data = _load_yaml(path)
    elif path.endswith(".json"):
        with open(path, "r") as f:
            config_data = json.load(f)
    else:
        raise ValueError("Unsupported file format")

    # Parse into ConstraintConfig
    config = ConstraintConfig(**config_data)

    # Process includes
    if hasattr(config, "includes") and config.includes:
        included_constraints = []
        for include_path in config.includes:
            # Resolve relative paths
            if not os.path.isabs(include_path):
                include_path = os.path.join(os.path.dirname(path), include_path)
            included_constraints.extend(load_constraints_from_file(include_path))

        # Merge constraints (deduplicate by name)
        constraint_map = {c.name: c for c in config.constraints}
        for constraint in included_constraints:
            if constraint.name not in constraint_map:
                constraint_map[constraint.name] = constraint
        config.constraints = list(constraint_map.values())

    # Compute input hash for each constraint
    for constraint in config.constraints:
        constraint_json = json.dumps(constraint.dict(), sort_keys=True)
        constraint.input_hash = hashlib.sha256(constraint_json.encode()).hexdigest()

    return config.constraints
