import pytest

from app.core.config import Settings
from app.providers.ai import ChatMessage
from app.providers.ai.deterministic import DeterministicEmbeddingProvider
from app.providers.ai.factory import (
    get_chat_completion_provider,
    get_embedding_provider,
)


def test_local_provider_can_embed_and_complete_without_api_key():
    settings = Settings(ai_provider="test", ai_embedding_dimensions=8, ai_api_key=None)

    embedding_provider = get_embedding_provider(settings)
    chat_provider = get_chat_completion_provider(settings)

    assert isinstance(embedding_provider, DeterministicEmbeddingProvider)
    assert len(embedding_provider.embed_texts(["blocked drain"])[0]) == 8
    assert (
        chat_provider.complete([ChatMessage(role="user", content="Do you service Sydney?")])
        == "Deterministic response: Do you service Sydney?"
    )


def test_openai_compatible_provider_requires_api_key():
    settings = Settings(ai_provider="openai-compatible", ai_api_key=None)

    with pytest.raises(RuntimeError, match="AI_API_KEY"):
        get_embedding_provider(settings)
