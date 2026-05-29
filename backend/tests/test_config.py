from app.core.config import Settings, get_settings, parse_bool, parse_csv
from app.db.config import get_database_url


def test_parse_bool_handles_common_values():
    assert parse_bool("true") is True
    assert parse_bool("YES") is True
    assert parse_bool("0") is False
    assert parse_bool(None, default=True) is True


def test_parse_csv_handles_widget_origins():
    assert parse_csv("https://a.test, https://b.test") == [
        "https://a.test",
        "https://b.test",
    ]
    assert parse_csv(None, ["*"]) == ["*"]


def test_settings_do_not_require_ai_secret_for_local_startup():
    get_settings.cache_clear()
    settings = get_settings()

    assert settings.ai_provider == "openai-compatible"
    assert settings.ai_api_key is None


def test_database_url_placeholder_is_available():
    get_settings.cache_clear()

    assert get_database_url().startswith("postgresql+psycopg://")


def test_production_validation_requires_operational_secrets(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_LOG_FORMAT", "text")
    monkeypatch.setenv("BUSINESS_PORTAL_SESSION_SECRET", "change-me-before-production")
    monkeypatch.setenv("ADMIN_PORTAL_SESSION_SECRET", "change-me-before-production")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("ENABLE_API_DOCS", "true")
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "false")
    monkeypatch.setenv("RATE_LIMIT_BACKEND", "memory")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://ai_tradie:ai_tradie@postgres:5432/ai_tradie",
    )
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    monkeypatch.setenv("AI_API_KEY", "")
    monkeypatch.setenv("EMAIL_PROVIDER", "console")
    monkeypatch.setenv("PUBLIC_BASE_URL", "http://example.test")
    monkeypatch.setenv("NEXT_PUBLIC_API_BASE_URL", "http://127.0.0.1:8000")
    monkeypatch.setenv("BACKUP_ENCRYPTION_PASSPHRASE", "short")

    issues = Settings().production_security_issues()

    assert "BUSINESS_PORTAL_SESSION_SECRET must be set to a strong secret" in issues
    assert "ADMIN_PORTAL_SESSION_SECRET must be set to a strong secret" in issues
    assert "AUTH_COOKIE_SECURE must be true in production" in issues
    assert "CORS_ALLOWED_ORIGINS must use https origins in production" in issues
    assert "ENABLE_API_DOCS must be false in production" in issues
    assert "APP_LOG_FORMAT must be json in production" in issues
    assert "RATE_LIMIT_BACKEND must be redis in production" in issues
    assert "DATABASE_URL must not use default or placeholder credentials" in issues
    assert "REDIS_URL must use the private Docker/service hostname in production" in issues
    assert "AI_API_KEY must be set for the OpenAI-compatible provider" in issues
    assert "EMAIL_PROVIDER must be smtp in production" in issues
    assert "PUBLIC_BASE_URL must be an https URL in production" in issues
    assert "NEXT_PUBLIC_API_BASE_URL must be /api when served through Nginx" in issues
    assert "BACKUP_ENCRYPTION_PASSPHRASE must be a strong secret" in issues


def test_production_validation_accepts_hardened_compose_settings(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.setenv("APP_LOG_FORMAT", "json")
    monkeypatch.setenv("ENABLE_API_DOCS", "false")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://example.test")
    monkeypatch.setenv("BUSINESS_PORTAL_SESSION_SECRET", "b" * 48)
    monkeypatch.setenv("ADMIN_PORTAL_SESSION_SECRET", "a" * 48)
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "true")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("WIDGET_REQUIRE_ALLOWED_ORIGINS", "true")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://ai_magnet:strong-password@postgres:5432/ai_magnet",
    )
    monkeypatch.setenv("REDIS_URL", "redis://redis:6379/0")
    monkeypatch.setenv("AI_API_KEY", "test-provider-key")
    monkeypatch.setenv("EMAIL_PROVIDER", "smtp")
    monkeypatch.setenv("SMTP_HOST", "smtp.example.test")
    monkeypatch.setenv("SMTP_USERNAME", "smtp-user")
    monkeypatch.setenv("SMTP_PASSWORD", "smtp-password")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "noreply@example.test")
    monkeypatch.setenv("SMTP_STARTTLS", "true")
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://example.test")
    monkeypatch.setenv("NEXT_PUBLIC_API_BASE_URL", "/api")
    monkeypatch.setenv("BACKUP_ENCRYPTION_PASSPHRASE", "p" * 48)

    assert Settings().production_security_issues() == []
