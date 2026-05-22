"""Database configuration helpers.

Phase 1 only exposes configuration placeholders. Connection management,
models, migrations, and tenant-aware repositories belong to Phase 2.
"""

from app.core.config import Settings, get_settings


def get_database_url(settings: Settings | None = None) -> str:
    """Return the configured database URL without opening a connection."""
    runtime_settings = settings or get_settings()
    return runtime_settings.database_url
