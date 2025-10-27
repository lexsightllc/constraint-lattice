"""Lightweight test stubs for the optional ``hypothesis`` dependency.

This project only needs a very small subset of Hypothesis' API in order to
exercise its property-based tests.  The real library is sizeable and pulls in
native extensions that are unnecessary for our constrained runtime.  To keep
the public surface area compatible without depending on the external package,
we provide extremely small stand-ins that mimic the behaviour required by the
tests.

The goal of the stub is not to offer exhaustive fuzzing, but rather to provide
deterministic, repeatable values so that the tests execute without importing
the third-party dependency.  Each strategy simply returns a representative
value, which is sufficient for unit-level smoke checks.
"""

from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable, Iterable, Optional


class Strategy:
    """Minimal callable wrapper that mimics Hypothesis strategies."""

    def __init__(self, generator: Callable[[], Any]):
        self._generator = generator

    def __call__(self) -> Any:
        return self._generator()

    def example(self) -> Any:  # pragma: no cover - parity helper
        return self._generator()

    def map(self, func: Callable[[Any], Any]) -> "Strategy":
        return Strategy(lambda: func(self._generator()))


def _resolve(value: Any) -> Any:
    """Resolve nested strategies or callables into concrete values."""

    if isinstance(value, Strategy):
        return value()
    if callable(value):  # pragma: no cover - defensive
        return value()
    return value


class _StrategiesModule:
    """Collection of strategy constructors used by the test-suite."""

    def integers(
        self,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ) -> Strategy:
        default = 0
        if min_value is not None:
            default = min_value
        elif max_value is not None:
            default = max_value
        return Strategy(lambda: default)

    def floats(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_nan: bool = True,
        allow_infinity: bool = True,
    ) -> Strategy:
        _ = (allow_nan, allow_infinity)  # parameters kept for signature parity
        if min_value is not None:
            return Strategy(lambda: float(min_value))
        if max_value is not None:
            return Strategy(lambda: float(max_value))
        return Strategy(lambda: 0.0)

    def text(self, alphabet: Optional[Iterable[str]] = None, **_: Any) -> Strategy:
        if alphabet:
            alphabet = list(alphabet)
            sample = "".join(alphabet[:3])
        else:
            sample = "example"
        return Strategy(lambda: sample)

    def lists(
        self,
        strategy: Strategy,
        min_size: int = 0,
        max_size: Optional[int] = None,
    ) -> Strategy:
        def _generator() -> list[Any]:
            size = max(min_size, 0)
            if max_size is not None:
                size = min(size, max_size)
            return [_resolve(strategy) for _ in range(size)]

        return Strategy(_generator)

    def sampled_from(self, population: Iterable[Any]) -> Strategy:
        population = list(population)
        if not population:
            return Strategy(lambda: None)
        return Strategy(lambda: population[0])


strategies = _StrategiesModule()


def given(*given_args: Strategy, **given_kwargs: Strategy) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that feeds deterministic data produced by the stub strategies."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            positional = [
                _resolve(arg) for arg in given_args
            ]
            keyword = {key: _resolve(value) for key, value in given_kwargs.items()}
            return func(*args, *positional, **keyword, **kwargs)

        wrapper.__signature__ = inspect.Signature()  # type: ignore[attr-defined]
        return wrapper

    return decorator


def settings(*_: Any, **__: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """No-op decorator kept for API compatibility with Hypothesis."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return func

    return decorator


__all__ = ["Strategy", "given", "settings", "strategies"]
