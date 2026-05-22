"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache


def parse_bool(value: str | None, default: bool = False) -> bool:
    """Parse common environment boolean strings."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_csv(value: str | None, default: list[str] | None = None) -> list[str]:
    """Parse a comma-separated environment variable into a string list."""
    if value is None:
        return list(default or [])
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    app_name: str = field(
        default_factory=lambda: os.getenv("APP_NAME", "AI Tradie Receptionist API")
    )
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "0.1.0"))
    environment: str = field(default_factory=lambda: os.getenv("APP_ENV", "local"))
    debug: bool = field(
        default_factory=lambda: parse_bool(os.getenv("APP_DEBUG"), default=False)
    )
    log_level: str = field(default_factory=lambda: os.getenv("APP_LOG_LEVEL", "INFO"))
    enable_api_docs: bool = field(
        default_factory=lambda: parse_bool(os.getenv("ENABLE_API_DOCS"), default=True)
    )
    cors_allowed_origins: list[str] = field(
        default_factory=lambda: parse_csv(os.getenv("CORS_ALLOWED_ORIGINS"), ["*"])
    )

    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://ai_tradie:ai_tradie@postgres:5432/ai_tradie",
        )
    )
    redis_url: str = field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://redis:6379/0")
    )

    ai_provider: str = field(
        default_factory=lambda: os.getenv("AI_PROVIDER", "openai-compatible")
    )
    ai_api_base_url: str = field(
        default_factory=lambda: os.getenv(
            "AI_API_BASE_URL", "https://api.openai.com/v1"
        )
    )
    ai_api_key: str | None = field(
        default_factory=lambda: os.getenv("AI_API_KEY") or None
    )
    ai_embedding_model: str = field(
        default_factory=lambda: os.getenv("AI_EMBEDDING_MODEL", "text-embedding-3-small")
    )
    ai_chat_model: str = field(
        default_factory=lambda: os.getenv("AI_CHAT_MODEL", "gpt-4.1-mini")
    )
    ai_embedding_dimensions: int = field(
        default_factory=lambda: int(os.getenv("AI_EMBEDDING_DIMENSIONS", "1536"))
    )

    rag_chunk_size: int = field(
        default_factory=lambda: int(os.getenv("RAG_CHUNK_SIZE", "700"))
    )
    rag_chunk_overlap: int = field(
        default_factory=lambda: int(os.getenv("RAG_CHUNK_OVERLAP", "100"))
    )
    rag_top_k: int = field(default_factory=lambda: int(os.getenv("RAG_TOP_K", "5")))


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
