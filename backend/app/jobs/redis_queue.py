"""Redis wake signal for the durable database job queue."""

from __future__ import annotations

import logging

from app.core.config import Settings


logger = logging.getLogger(__name__)


class RedisWakeQueue:
    """Small Redis list wrapper used to wake workers for durable DB jobs."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from redis import Redis

            self._client = Redis.from_url(
                self.settings.redis_url,
                socket_timeout=5,
                socket_connect_timeout=5,
                decode_responses=True,
            )
        return self._client

    def notify(self, job_id: str) -> bool:
        """Push a job id signal to Redis without treating Redis as source of truth."""
        try:
            self.client.rpush(self.settings.worker_redis_queue_key, job_id)
        except Exception as exc:
            logger.warning("Failed to publish background job wake signal: %s", exc)
            return False
        return True

    def wait(self, timeout_seconds: int) -> str | None:
        """Block briefly waiting for a wake signal."""
        try:
            item = self.client.blpop(
                [self.settings.worker_redis_queue_key],
                timeout=max(timeout_seconds, 1),
            )
        except Exception as exc:
            logger.warning("Failed to wait for background job wake signal: %s", exc)
            return None
        if not item:
            return None
        _queue_name, job_id = item
        return str(job_id)

    def ping(self) -> bool:
        """Return true if Redis is reachable."""
        try:
            return bool(self.client.ping())
        except Exception:
            return False
