# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 ochoaughini. All rights reserved.
# See LICENSE for full terms.

import logging
import os
from typing import Any, Dict, Optional, Tuple

try:
    import torch  # type: ignore
except Exception:  # pragma: no cover - allow tests without torch
    torch = None  # type: ignore

try:
    from prometheus_client import Counter, Histogram
except ImportError:  # pragma: no cover

    class _NoMetrics:
        def __init__(self, *args, **kwargs):
            pass

        def inc(self, *args, **kwargs):
            pass

        def time(self):  # context manager
            class _NoopCtx:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    pass

            return _NoopCtx()

    Counter = Histogram = _NoMetrics  # type: ignore

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        pipeline,
    )

    pl = pipeline
except ModuleNotFoundError:  # pragma: no cover
    AutoModelForCausalLM = None
    AutoTokenizer = None
    BitsAndBytesConfig = None
    pipeline = None
    pl = None

logger = logging.getLogger(__name__)


class ConstraintPhi2Moderation:
    """
    Content moderation constraint using Microsoft's Phi-2 model
    """

    def __init__(
        self,
        model_name: str = "microsoft/phi-2",
        device: Optional[str] = None,
        safety_threshold: float = 0.7,
        quantize: bool = False,
        fallback_strategy: str = "mask",
    ):
        """
        Initialize Phi-2 moderation constraint
        """
        self.model_name = model_name
        if torch is not None and torch.cuda.is_available():
            default_device = "cuda"
        else:
            default_device = "cpu"
        self.device = device or default_device
        self.quantize = quantize
        self.safety_threshold = safety_threshold
        self.fallback_strategy = fallback_strategy

        load_real_model = (
            AutoTokenizer is not None
            and AutoModelForCausalLM is not None
            and os.environ.get("CL_USE_PHI2")
        )

        if load_real_model:
            # Initialize tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True
            )
            # Initialize model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, trust_remote_code=True
            )
            if quantize and torch is not None:
                self.model = torch.quantization.quantize_dynamic(
                    self.model, {torch.nn.Linear}, dtype=torch.qint8
                )
            self.model = self.model.to(self.device)
        else:  # pragma: no cover - transformers missing or offline stub
            self.tokenizer = None
            self.model = None
        self.logger = logging.getLogger(__name__)

    def apply_constraints(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Apply Phi-2 moderation to input text

        :return: Tuple (is_safe, violation_reason)
        """
        try:
            if self.tokenizer is None or self.model is None:
                return True, None

            # Prepare moderation prompt
            prompt = f"Classify the following text as 'safe' or 'unsafe':\n{text}\nClassification:"

            # Tokenize and generate
            inputs = self.tokenizer(
                prompt, return_tensors="pt", truncation=True, max_length=512
            )
            if torch is not None:
                inputs = inputs.to(self.device)
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits = outputs.logits
            else:
                outputs = self.model(**inputs)
                logits = outputs.logits

            # Get probabilities for 'safe' and 'unsafe' tokens
            safe_token_id = self.tokenizer.encode("safe")[0]
            unsafe_token_id = self.tokenizer.encode("unsafe")[0]

            last_token_logits = logits[0, -1, :]
            probs = (
                torch.softmax(last_token_logits, dim=-1)
                if torch is not None
                else last_token_logits.softmax(dim=-1)
            )

            safe_prob = probs[safe_token_id].item()
            unsafe_prob = probs[unsafe_token_id].item()

            # Determine safety based on threshold
            if unsafe_prob > self.safety_threshold:
                return False, (
                    f"Unsafe content detected (confidence: {unsafe_prob:.2f})"
                )
            return True, None

        except Exception as e:
            self.logger.error(f"Phi-2 moderation failed: {str(e)}")
            # Fallback: Return safe but log error
            return True, None

    def _analyse(self, text: str) -> Dict[str, Any]:
        is_safe, reason = self.apply_constraints(text)
        violations: Dict[str, float] = {}
        if not is_safe and reason:
            violations["policy_violation"] = 1.0
        return {"is_safe": is_safe, "violations": violations, "reason": reason}

    def _regenerate(self, text: str, analysis: Dict[str, Any]) -> str:
        """Generate a simple safe replacement when regeneration is requested."""

        return "[Content adapted by Phi-2 moderation]"

    def moderate(self, text: str) -> str:
        """Moderate ``text`` according to the configured fallback strategy."""

        analysis = self._analyse(text)
        if analysis.get("is_safe", True):
            return text

        strategy = self.fallback_strategy.lower()
        if strategy == "block":
            reason = analysis.get("reason") or "Policy violation"
            return f"[Content removed: {reason}]"
        if strategy == "mask":
            return "[REDACTED]"
        if strategy == "regenerate":
            return self._regenerate(text, analysis)
        return text

    def __repr__(self) -> str:
        return f"ConstraintPhi2Moderation(model='{self.model_name}', threshold={self.safety_threshold})"


if __name__ == "__main__":
    moderator = ConstraintPhi2Moderation()
    test_cases = [
        "What's the weather like today?",
        "How can I harm someone?",
        "Tell me a joke",
        "Explain how to steal a car",
    ]
    for text in test_cases:
        result = moderator.apply_constraints(text)
        print(f"Text: '{text}'\nSafe: {result}\n")
