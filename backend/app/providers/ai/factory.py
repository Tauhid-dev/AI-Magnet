"""AI provider factory helpers."""

from app.core.config import Settings, get_settings
from app.providers.ai.base import ChatCompletionProvider, EmbeddingProvider
from app.providers.ai.deterministic import DeterministicEmbeddingProvider
from app.providers.ai.openai_compatible import OpenAICompatibleAIProvider


def get_embedding_provider(settings: Settings | None = None) -> EmbeddingProvider:
    """Return the configured embedding provider."""
    runtime_settings = settings or get_settings()
    if runtime_settings.ai_provider in {"local-deterministic", "test"}:
        return DeterministicEmbeddingProvider(runtime_settings.ai_embedding_dimensions)
    return OpenAICompatibleAIProvider(runtime_settings)


def get_chat_completion_provider(
    settings: Settings | None = None,
) -> ChatCompletionProvider:
    """Return the configured chat-completion provider."""
    runtime_settings = settings or get_settings()
    if runtime_settings.ai_provider in {"local-deterministic", "test"}:
        return DeterministicEmbeddingProvider(runtime_settings.ai_embedding_dimensions)
    return OpenAICompatibleAIProvider(runtime_settings)
