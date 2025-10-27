"""Lightweight dual-generation demo used by the test-suite.

The real script wires Hugging Face pipelines together.  For tests we only need
to exercise the orchestration logic and emit a trace file so we provide a tiny
stub that is easy to patch.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, List

_MODELS: Iterable[str] = ("google/gemma-2b", "microsoft/phi-2")


def _load_pipeline(model_name: str, device: str = "cpu") -> Callable[[str], List[dict]]:
    """Load a text-generation pipeline.

    In production this would call :func:`transformers.pipeline`.  For the tests we
    raise a clear error so the call can be patched with a stub.
    """

    raise RuntimeError(
        "transformers pipeline is not available in the test environment"
    )


def _generate(prompt: str, device: str = "cpu") -> List[dict]:
    """Generate text with a pair of models and persist a trace file."""

    results: List[dict] = []
    for model in _MODELS:
        pipeline = _load_pipeline(model, device=device)
        outputs = pipeline(prompt, device=device, model=model)
        if not outputs:
            continue
        results.append({"model": model, "output": outputs[0]["generated_text"]})

    trace_dir = Path("results")
    trace_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    trace_path = trace_dir / f"dual_gen_{timestamp}.trace.json"
    trace_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


__all__ = ["_generate", "_load_pipeline"]
