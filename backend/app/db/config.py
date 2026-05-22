"""Database configuration helpers."""

from app.core.config import Settings, get_settings


def get_database_url(settings: Settings | None = None) -> str:
    """Return the configured database URL without opening a connection."""
    runtime_settings = settings or get_settings()
    return runtime_settings.database_url
