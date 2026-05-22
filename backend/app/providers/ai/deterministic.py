"""Deterministic local AI providers for tests and offline development."""

from __future__ import annotations

import hashlib
import math

from app.providers.ai.base import ChatMessage


class DeterministicEmbeddingProvider:
    """Local AI provider that creates stable outputs without network calls."""

    def __init__(self, dimensions: int = 32) -> None:
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def complete(self, messages: list[ChatMessage]) -> str:
        """Return a deterministic response for tests and local smoke checks."""
        last_user_message = next(
            (message.content for message in reversed(messages) if message.role == "user"),
            "",
        )
        return f"Deterministic response: {last_user_message}".strip()

    def _embed(self, text: str) -> list[float]:
        vector = [0.0 for _ in range(self.dimensions)]
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += 1.0
        magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / magnitude for value in vector]
