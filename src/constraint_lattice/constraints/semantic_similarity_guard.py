# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 ochoaughini. All rights reserved.
# See LICENSE for full terms.

import os
from typing import Callable, Optional

import numpy as np

class SemanticSimilarityGuard:
    """
    Vector-space similarity filter.  When a reference embedding is supplied it
    blocks inputs whose cosine similarity falls below the chosen threshold; when
    no reference is supplied it operates in inert mode and allows everything.
    """

    def __init__(
        self,
        reference: Optional[str] = None,
        threshold: float = 0.85,
        tau: Optional[float] = None,
    ):
        self.threshold = tau if tau is not None else threshold
        self.active = reference is not None

        self._encoder: Optional[Callable[[str], np.ndarray]] = None
        self.model = None
        self.reference_vector: Optional[np.ndarray] = None

        if self.active:
            self._encoder = self._load_encoder()
            self.reference_vector = self._encoder(reference or "")

    def apply(self, text: str) -> bool:
        """
        Return True when the text is sufficiently similar to the reference or
        when the guard is inert; otherwise return False.
        """
        if not self.active:
            return True

        input_vector = self._encoder(text) if self._encoder else None
        if input_vector is None or self.reference_vector is None:
            return True

        similarity = self._cosine_similarity(input_vector, self.reference_vector)
        return similarity >= self.threshold

    def filter_constraint(self, prompt: str, text: str) -> str:
        """API-compatible wrapper used by the constraint engine tests."""

        return text if self.apply(text) else ""

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def _load_encoder(self) -> Callable[[str], np.ndarray]:
        """Return a sentence embedding callable with an offline fallback."""

        if not os.environ.get("CL_USE_SENTENCE_TRANSFORMER"):
            self.model = None
            return self._fallback_encode

        try:  # pragma: no cover - exercised indirectly in tests
            from sentence_transformers import SentenceTransformer

            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            self.model = SentenceTransformer(
                "all-MiniLM-L6-v2", local_files_only=True
            )
            return self.model.encode
        except Exception:  # pragma: no cover - offline environment fallback
            self.model = None
            return self._fallback_encode

    @staticmethod
    def _fallback_encode(text: str) -> np.ndarray:
        """Map a string to a deterministic embedding without network access."""

        vector = np.zeros(16, dtype=np.float32)
        for idx, byte in enumerate(text.encode("utf-8")):
            vector[idx % vector.size] += byte

        norm = np.linalg.norm(vector)
        if norm:
            vector /= norm
        return vector
