"""OpenAI-compatible AI provider implementation."""

from __future__ import annotations

import httpx

from app.core.config import Settings
from app.providers.ai.base import ChatMessage


class OpenAICompatibleAIProvider:
    """Minimal OpenAI-compatible client for embeddings and chat completions."""

    def __init__(self, settings: Settings) -> None:
        if not settings.ai_api_key:
            raise RuntimeError("AI_API_KEY is required for OpenAI-compatible provider")
        self.base_url = settings.ai_api_base_url.rstrip("/")
        self.api_key = settings.ai_api_key
        self.embedding_model = settings.ai_embedding_model
        self.chat_model = settings.ai_chat_model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        with self._client() as client:
            response = client.post(
                f"{self.base_url}/embeddings",
                json={"model": self.embedding_model, "input": texts},
            )
        response.raise_for_status()
        payload = response.json()
        data = sorted(payload["data"], key=lambda item: item["index"])
        return [item["embedding"] for item in data]

    def complete(self, messages: list[ChatMessage]) -> str:
        with self._client() as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.chat_model,
                    "messages": [
                        {"role": message.role, "content": message.content}
                        for message in messages
                    ],
                },
            )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=30.0,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
