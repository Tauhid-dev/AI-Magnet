"""Small app-level rate limiting helpers for public and portal endpoints."""

from __future__ import annotations

import hashlib
import logging
import time
from collections import defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass

from fastapi import HTTPException, Request, status

from app.core.config import Settings


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RateLimitResult:
    """Outcome of a rate-limit check."""

    allowed: bool
    retry_after_seconds: int


class InMemoryRateLimiter:
    """Fixed-window-ish limiter that avoids external infrastructure dependencies.

    PR-02 uses this as the immediate application safety net. PR-04/PR-05 can add
    Nginx/Redis-backed limits for horizontally scaled production deployments.
    """

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, *, limit: int, window_seconds: int) -> RateLimitResult:
        if limit <= 0 or window_seconds <= 0:
            return RateLimitResult(allowed=True, retry_after_seconds=0)
        now = time.monotonic()
        cutoff = now - window_seconds
        events = self._events[key]
        while events and events[0] <= cutoff:
            events.popleft()
        if len(events) >= limit:
            retry_after = max(1, int(window_seconds - (now - events[0])))
            return RateLimitResult(allowed=False, retry_after_seconds=retry_after)
        events.append(now)
        return RateLimitResult(allowed=True, retry_after_seconds=0)

    def reset(self) -> None:
        """Clear limiter state for tests."""
        self._events.clear()


rate_limiter = InMemoryRateLimiter()


def client_ip(request: Request) -> str:
    """Return the apparent client IP without trusting spoofable proxy headers."""
    if request.client is None or not request.client.host:
        return "unknown"
    return request.client.host


def fingerprint(value: str) -> str:
    """Hash identifiers before using them in limiter keys or logs."""
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()[:24]


def rate_limit_key(scope: str, identifiers: Iterable[str]) -> str:
    """Build a non-PII limiter key."""
    parts = [scope]
    parts.extend(fingerprint(identifier) for identifier in identifiers if identifier)
    return ":".join(parts)


def enforce_rate_limit(
    request: Request,
    settings: Settings,
    *,
    scope: str,
    identifiers: Iterable[str] = (),
    limit: int,
    window_seconds: int | None = None,
) -> None:
    """Raise HTTP 429 when a request exceeds a configured policy."""
    if not settings.rate_limit_enabled:
        return
    window = window_seconds or settings.rate_limit_window_seconds
    key = rate_limit_key(scope, [client_ip(request), *identifiers])
    result = rate_limiter.check(key, limit=limit, window_seconds=window)
    if result.allowed:
        return
    logger.warning(
        "rate_limit_exceeded",
        extra={"scope": scope, "retry_after_seconds": result.retry_after_seconds},
    )
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many requests. Please wait before trying again.",
        headers={"Retry-After": str(result.retry_after_seconds)},
    )
