"""Stub implementations for :mod:`hypothesis.extra.numpy` used in tests."""

from __future__ import annotations

from typing import Any, Iterable, Tuple

import numpy as np

from .. import Strategy, _resolve


def arrays(
    dtype: Any,
    shape: Any,
    elements: Strategy | None = None,
) -> Strategy:
    """Return a deterministic array strategy.

    The real Hypothesis implementation produces many varied examples.  Our
    lightweight stub only needs to return a single array instance that matches
    the requested dtype and shape so downstream logic can execute.
    """

    def _generator() -> np.ndarray:
        resolved_shape = _resolve(shape)
        if isinstance(resolved_shape, int):
            resolved_shape = (resolved_shape,)
        elif isinstance(resolved_shape, Iterable) and not isinstance(
            resolved_shape, tuple
        ):
            resolved_shape = tuple(resolved_shape)
        elif not isinstance(resolved_shape, tuple):
            resolved_shape = (1,)

        fill_value = 0
        if elements is not None:
            fill_value = _resolve(elements)
        return np.full(resolved_shape, fill_value, dtype=dtype)

    return Strategy(_generator)


__all__ = ["arrays"]
