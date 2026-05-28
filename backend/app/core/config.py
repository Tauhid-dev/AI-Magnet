"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache


INSECURE_SECRET_VALUES = frozenset(
    {
        "",
        "change-me-before-production",
        "change-me-local-admin-portal-secret",
        "change-me-local-business-portal-secret",
    }
)


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
        default_factory=lambda: parse_csv(
            os.getenv("CORS_ALLOWED_ORIGINS"),
            ["http://127.0.0.1:3000", "http://localhost:3000"],
        )
    )
    business_portal_session_secret: str = field(
        default_factory=lambda: os.getenv(
            "BUSINESS_PORTAL_SESSION_SECRET",
            "change-me-local-business-portal-secret",
        )
    )
    business_portal_session_ttl_minutes: int = field(
        default_factory=lambda: int(os.getenv("BUSINESS_PORTAL_SESSION_TTL_MINUTES", "480"))
    )
    business_portal_cookie_name: str = field(
        default_factory=lambda: os.getenv(
            "BUSINESS_PORTAL_COOKIE_NAME",
            "ai_magnet_business_session",
        )
    )
    admin_portal_session_secret: str = field(
        default_factory=lambda: os.getenv(
            "ADMIN_PORTAL_SESSION_SECRET",
            "change-me-local-admin-portal-secret",
        )
    )
    admin_portal_session_ttl_minutes: int = field(
        default_factory=lambda: int(os.getenv("ADMIN_PORTAL_SESSION_TTL_MINUTES", "240"))
    )
    admin_portal_cookie_name: str = field(
        default_factory=lambda: os.getenv("ADMIN_PORTAL_COOKIE_NAME", "ai_magnet_admin_session")
    )
    auth_cookie_secure: bool = field(
        default_factory=lambda: parse_bool(os.getenv("AUTH_COOKIE_SECURE"), default=False)
    )
    auth_cookie_samesite: str = field(
        default_factory=lambda: os.getenv("AUTH_COOKIE_SAMESITE", "lax")
    )
    auth_failed_login_limit: int = field(
        default_factory=lambda: int(os.getenv("AUTH_FAILED_LOGIN_LIMIT", "5"))
    )
    auth_lockout_minutes: int = field(
        default_factory=lambda: int(os.getenv("AUTH_LOCKOUT_MINUTES", "15"))
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

    email_provider: str = field(
        default_factory=lambda: os.getenv("EMAIL_PROVIDER", "console")
    )
    smtp_host: str | None = field(default_factory=lambda: os.getenv("SMTP_HOST") or None)
    smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_username: str | None = field(default_factory=lambda: os.getenv("SMTP_USERNAME") or None)
    smtp_password: str | None = field(default_factory=lambda: os.getenv("SMTP_PASSWORD") or None)
    smtp_from_email: str | None = field(
        default_factory=lambda: os.getenv("SMTP_FROM_EMAIL") or None
    )
    smtp_use_tls: bool = field(
        default_factory=lambda: parse_bool(os.getenv("SMTP_USE_TLS"), default=False)
    )
    smtp_starttls: bool = field(
        default_factory=lambda: parse_bool(os.getenv("SMTP_STARTTLS"), default=True)
    )

    def production_security_issues(self) -> list[str]:
        """Return production-only configuration issues."""
        if self.environment.strip().lower() not in {"prod", "production"}:
            return []
        issues: list[str] = []
        if self.business_portal_session_secret in INSECURE_SECRET_VALUES:
            issues.append("BUSINESS_PORTAL_SESSION_SECRET must be set to a strong secret")
        if self.admin_portal_session_secret in INSECURE_SECRET_VALUES:
            issues.append("ADMIN_PORTAL_SESSION_SECRET must be set to a strong secret")
        if "*" in self.cors_allowed_origins:
            issues.append("CORS_ALLOWED_ORIGINS must not contain '*' in production")
        if self.enable_api_docs:
            issues.append("ENABLE_API_DOCS must be false in production")
        return issues

    def validate_runtime_security(self) -> None:
        """Raise if production configuration is unsafe."""
        issues = self.production_security_issues()
        if issues:
            raise RuntimeError(
                "Production security configuration invalid: " + "; ".join(issues)
            )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
