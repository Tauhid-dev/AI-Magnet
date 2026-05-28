"""Worker container dependency health check."""

from __future__ import annotations

import sys

from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import get_engine_for_url
from app.jobs.redis_queue import RedisWakeQueue


def main() -> int:
    """Return 0 when the worker can reach its backing services."""
    settings = get_settings()
    try:
        with get_engine_for_url(settings.database_url, settings.debug).connect() as connection:
            connection.execute(text("SELECT 1"))
        if not RedisWakeQueue(settings).ping():
            return 1
    except Exception:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
