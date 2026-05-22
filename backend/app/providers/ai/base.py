"""Provider interfaces for AI services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ChatMessage:
    """Message passed to a chat-completion provider."""

    role: str
    content: str


class EmbeddingProvider(Protocol):
    """Embeds text into numeric vectors."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text."""


class ChatCompletionProvider(Protocol):
    """Generates chat completions."""

    def complete(self, messages: list[ChatMessage]) -> str:
        """Return the assistant response text."""


class AIProvider(EmbeddingProvider, ChatCompletionProvider, Protocol):
    """Provider that supports the Phase 3 AI operations."""
