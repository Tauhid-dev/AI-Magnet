"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache


INSECURE_SECRET_VALUES = frozenset(
    {
        "",
        "change-me",
        "change-me-before-production",
        "change-me-local-admin-portal-secret",
        "change-me-local-business-portal-secret",
        "replace-with-strong-random-secret",
        "replace-with-strong-random-password",
        "replace-with-provider-api-key",
        "replace-with-smtp-password",
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


def is_placeholder(value: str | None) -> bool:
    """Return true when a production value is blank or clearly a placeholder."""
    if value is None:
        return True
    normalized = value.strip().lower()
    if normalized in INSECURE_SECRET_VALUES:
        return True
    return any(marker in normalized for marker in ("change-me", "replace-with", "placeholder"))


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
    log_format: str = field(default_factory=lambda: os.getenv("APP_LOG_FORMAT", "text"))
    request_id_header: str = field(
        default_factory=lambda: os.getenv("REQUEST_ID_HEADER", "X-Request-ID")
    )
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
    rate_limit_enabled: bool = field(
        default_factory=lambda: parse_bool(os.getenv("RATE_LIMIT_ENABLED"), default=True)
    )
    rate_limit_window_seconds: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    )
    rate_limit_login_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_LOGIN_PER_MINUTE", "20"))
    )
    rate_limit_widget_init_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_WIDGET_INIT_PER_MINUTE", "120"))
    )
    rate_limit_chat_start_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_CHAT_START_PER_MINUTE", "60"))
    )
    rate_limit_chat_message_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_CHAT_MESSAGE_PER_MINUTE", "120"))
    )
    rate_limit_portal_write_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_PORTAL_WRITE_PER_MINUTE", "60"))
    )
    rate_limit_admin_write_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_ADMIN_WRITE_PER_MINUTE", "30"))
    )
    widget_require_allowed_origins: bool = field(
        default_factory=lambda: parse_bool(
            os.getenv("WIDGET_REQUIRE_ALLOWED_ORIGINS"),
            default=False,
        )
    )
    privacy_default_retention_days: int = field(
        default_factory=lambda: int(os.getenv("PRIVACY_DEFAULT_RETENTION_DAYS", "30"))
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
    worker_queue_name: str = field(
        default_factory=lambda: os.getenv("WORKER_QUEUE_NAME", "default")
    )
    worker_redis_queue_key: str = field(
        default_factory=lambda: os.getenv("WORKER_REDIS_QUEUE_KEY", "ai-magnet:jobs:default")
    )
    worker_poll_interval_seconds: int = field(
        default_factory=lambda: int(os.getenv("WORKER_POLL_INTERVAL_SECONDS", "5"))
    )
    worker_heartbeat_interval_seconds: int = field(
        default_factory=lambda: int(os.getenv("WORKER_HEARTBEAT_INTERVAL_SECONDS", "15"))
    )
    worker_job_lock_timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("WORKER_JOB_LOCK_TIMEOUT_SECONDS", "900"))
    )
    worker_default_max_attempts: int = field(
        default_factory=lambda: int(os.getenv("WORKER_DEFAULT_MAX_ATTEMPTS", "3"))
    )
    worker_retry_base_seconds: int = field(
        default_factory=lambda: int(os.getenv("WORKER_RETRY_BASE_SECONDS", "30"))
    )
    worker_retry_max_seconds: int = field(
        default_factory=lambda: int(os.getenv("WORKER_RETRY_MAX_SECONDS", "300"))
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
    website_crawl_user_agent: str = field(
        default_factory=lambda: os.getenv(
            "WEBSITE_CRAWL_USER_AGENT",
            "AI-MagnetBot/0.1 (+https://example.com/ai-magnet-bot)",
        )
    )
    website_crawl_timeout_seconds: float = field(
        default_factory=lambda: float(os.getenv("WEBSITE_CRAWL_TIMEOUT_SECONDS", "10"))
    )
    website_crawl_max_pages: int = field(
        default_factory=lambda: int(os.getenv("WEBSITE_CRAWL_MAX_PAGES", "10"))
    )
    website_crawl_max_depth: int = field(
        default_factory=lambda: int(os.getenv("WEBSITE_CRAWL_MAX_DEPTH", "1"))
    )
    website_crawl_max_bytes: int = field(
        default_factory=lambda: int(os.getenv("WEBSITE_CRAWL_MAX_BYTES", "1048576"))
    )
    website_crawl_max_redirects: int = field(
        default_factory=lambda: int(os.getenv("WEBSITE_CRAWL_MAX_REDIRECTS", "5"))
    )
    website_crawl_respect_robots: bool = field(
        default_factory=lambda: parse_bool(os.getenv("WEBSITE_CRAWL_RESPECT_ROBOTS"), default=True)
    )
    document_storage_root: str = field(
        default_factory=lambda: os.getenv("DOCUMENT_STORAGE_ROOT", "storage/documents")
    )
    document_upload_max_bytes: int = field(
        default_factory=lambda: int(os.getenv("DOCUMENT_UPLOAD_MAX_BYTES", "10485760"))
    )
    document_upload_max_pages: int = field(
        default_factory=lambda: int(os.getenv("DOCUMENT_UPLOAD_MAX_PAGES", "50"))
    )
    document_ocr_enabled: bool = field(
        default_factory=lambda: parse_bool(os.getenv("DOCUMENT_OCR_ENABLED"), default=False)
    )
    document_malware_scan_mode: str = field(
        default_factory=lambda: os.getenv("DOCUMENT_MALWARE_SCAN_MODE", "basic")
    )

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
    public_base_url: str | None = field(
        default_factory=lambda: os.getenv("PUBLIC_BASE_URL") or None
    )
    frontend_api_base_url: str | None = field(
        default_factory=lambda: os.getenv("NEXT_PUBLIC_API_BASE_URL") or None
    )
    backup_encryption_passphrase: str | None = field(
        default_factory=lambda: os.getenv("BACKUP_ENCRYPTION_PASSPHRASE") or None
    )

    def production_security_issues(self) -> list[str]:
        """Return production-only configuration issues."""
        if self.environment.strip().lower() not in {"prod", "production"}:
            return []
        issues: list[str] = []
        if is_placeholder(self.business_portal_session_secret) or len(
            self.business_portal_session_secret
        ) < 32:
            issues.append("BUSINESS_PORTAL_SESSION_SECRET must be set to a strong secret")
        if is_placeholder(self.admin_portal_session_secret) or len(
            self.admin_portal_session_secret
        ) < 32:
            issues.append("ADMIN_PORTAL_SESSION_SECRET must be set to a strong secret")
        if not self.auth_cookie_secure:
            issues.append("AUTH_COOKIE_SECURE must be true in production")
        if self.auth_cookie_samesite.lower() not in {"lax", "strict", "none"}:
            issues.append("AUTH_COOKIE_SAMESITE must be lax, strict, or none")
        if "*" in self.cors_allowed_origins:
            issues.append("CORS_ALLOWED_ORIGINS must not contain '*' in production")
        if any(not origin.startswith("https://") for origin in self.cors_allowed_origins):
            issues.append("CORS_ALLOWED_ORIGINS must use https origins in production")
        if self.enable_api_docs:
            issues.append("ENABLE_API_DOCS must be false in production")
        if self.debug:
            issues.append("APP_DEBUG must be false in production")
        if self.log_format.strip().lower() != "json":
            issues.append("APP_LOG_FORMAT must be json in production")
        if not self.rate_limit_enabled:
            issues.append("RATE_LIMIT_ENABLED must be true in production")
        if self.rate_limit_window_seconds <= 0:
            issues.append("RATE_LIMIT_WINDOW_SECONDS must be greater than 0 in production")
        if self.rate_limit_login_per_minute <= 0:
            issues.append("RATE_LIMIT_LOGIN_PER_MINUTE must be greater than 0 in production")
        if self.rate_limit_widget_init_per_minute <= 0:
            issues.append("RATE_LIMIT_WIDGET_INIT_PER_MINUTE must be greater than 0 in production")
        if self.rate_limit_chat_start_per_minute <= 0:
            issues.append("RATE_LIMIT_CHAT_START_PER_MINUTE must be greater than 0 in production")
        if self.rate_limit_chat_message_per_minute <= 0:
            issues.append("RATE_LIMIT_CHAT_MESSAGE_PER_MINUTE must be greater than 0 in production")
        if not self.widget_require_allowed_origins:
            issues.append("WIDGET_REQUIRE_ALLOWED_ORIGINS must be true in production")
        if self.privacy_default_retention_days <= 0:
            issues.append("PRIVACY_DEFAULT_RETENTION_DAYS must be greater than 0 in production")
        if is_placeholder(self.database_url) or self.database_url.startswith("sqlite"):
            issues.append("DATABASE_URL must point to production PostgreSQL")
        if "ai_tradie:ai_tradie" in self.database_url or "change-me" in self.database_url:
            issues.append("DATABASE_URL must not use default or placeholder credentials")
        if not self.redis_url.startswith(("redis://", "rediss://")):
            issues.append("REDIS_URL must be a redis:// or rediss:// URL")
        if "localhost" in self.redis_url or "127.0.0.1" in self.redis_url:
            issues.append("REDIS_URL must use the private Docker/service hostname in production")
        if not self.worker_queue_name.strip():
            issues.append("WORKER_QUEUE_NAME must be set in production")
        if not self.worker_redis_queue_key.strip():
            issues.append("WORKER_REDIS_QUEUE_KEY must be set in production")
        if self.worker_poll_interval_seconds <= 0:
            issues.append("WORKER_POLL_INTERVAL_SECONDS must be greater than 0 in production")
        if self.worker_heartbeat_interval_seconds <= 0:
            issues.append("WORKER_HEARTBEAT_INTERVAL_SECONDS must be greater than 0 in production")
        if self.worker_job_lock_timeout_seconds <= 0:
            issues.append("WORKER_JOB_LOCK_TIMEOUT_SECONDS must be greater than 0 in production")
        if self.worker_default_max_attempts <= 0:
            issues.append("WORKER_DEFAULT_MAX_ATTEMPTS must be greater than 0 in production")
        if self.worker_retry_base_seconds < 0:
            issues.append("WORKER_RETRY_BASE_SECONDS must be zero or greater in production")
        if self.worker_retry_max_seconds < self.worker_retry_base_seconds:
            issues.append("WORKER_RETRY_MAX_SECONDS must be greater than or equal to base retry")
        if self.website_crawl_timeout_seconds <= 0:
            issues.append("WEBSITE_CRAWL_TIMEOUT_SECONDS must be greater than 0 in production")
        if self.website_crawl_max_pages <= 0:
            issues.append("WEBSITE_CRAWL_MAX_PAGES must be greater than 0 in production")
        if self.website_crawl_max_depth < 0:
            issues.append("WEBSITE_CRAWL_MAX_DEPTH must be zero or greater in production")
        if self.website_crawl_max_bytes <= 0:
            issues.append("WEBSITE_CRAWL_MAX_BYTES must be greater than 0 in production")
        if self.website_crawl_max_redirects < 0:
            issues.append("WEBSITE_CRAWL_MAX_REDIRECTS must be zero or greater in production")
        if not self.website_crawl_user_agent.strip():
            issues.append("WEBSITE_CRAWL_USER_AGENT must be set in production")
        if not self.document_storage_root.strip():
            issues.append("DOCUMENT_STORAGE_ROOT must be set in production")
        if self.document_upload_max_bytes <= 0:
            issues.append("DOCUMENT_UPLOAD_MAX_BYTES must be greater than 0 in production")
        if self.document_upload_max_pages <= 0:
            issues.append("DOCUMENT_UPLOAD_MAX_PAGES must be greater than 0 in production")
        if self.document_malware_scan_mode not in {"basic", "external", "disabled"}:
            issues.append("DOCUMENT_MALWARE_SCAN_MODE must be basic, external, or disabled")
        if self.document_malware_scan_mode == "disabled":
            issues.append("DOCUMENT_MALWARE_SCAN_MODE must not be disabled in production")
        if self.ai_provider == "openai-compatible" and is_placeholder(self.ai_api_key):
            issues.append("AI_API_KEY must be set for the OpenAI-compatible provider")
        if self.email_provider != "smtp":
            issues.append("EMAIL_PROVIDER must be smtp in production")
        if is_placeholder(self.smtp_host):
            issues.append("SMTP_HOST must be set in production")
        if self.smtp_port <= 0:
            issues.append("SMTP_PORT must be greater than 0 in production")
        if is_placeholder(self.smtp_username):
            issues.append("SMTP_USERNAME must be set in production")
        if is_placeholder(self.smtp_password):
            issues.append("SMTP_PASSWORD must be set in production")
        if is_placeholder(self.smtp_from_email):
            issues.append("SMTP_FROM_EMAIL must be set in production")
        if not (self.smtp_use_tls or self.smtp_starttls):
            issues.append("SMTP_USE_TLS or SMTP_STARTTLS must be true in production")
        if is_placeholder(self.public_base_url) or not self.public_base_url.startswith("https://"):
            issues.append("PUBLIC_BASE_URL must be an https URL in production")
        if self.frontend_api_base_url not in {"/api", None}:
            issues.append("NEXT_PUBLIC_API_BASE_URL must be /api when served through Nginx")
        if is_placeholder(self.backup_encryption_passphrase) or len(
            self.backup_encryption_passphrase or ""
        ) < 32:
            issues.append("BACKUP_ENCRYPTION_PASSPHRASE must be a strong secret")
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
