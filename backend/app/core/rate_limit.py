"""Application-level rate limiting helpers for public and portal endpoints."""

from __future__ import annotations

import hashlib
import logging
import re
import time
from collections import defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Protocol

from fastapi import HTTPException, Request, status

from app.core.config import Settings

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)

REQUEST_ID_HEADERS = ("x-request-id", "x-correlation-id")
SAFE_REQUEST_ID_RE = re.compile(
    r"^(?:[0-9a-fA-F]{16,64}|"
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}|"
    r"[0-9A-HJKMNP-TV-Z]{26})$"
)


@dataclass(frozen=True)
class RateLimitResult:
    """Outcome of a rate-limit check."""

    allowed: bool
    retry_after_seconds: int


class RateLimiter(Protocol):
    """Shared rate-limiter interface."""

    def check(self, key: str, *, limit: int, window_seconds: int) -> RateLimitResult:
        """Return whether the request is allowed for the key/window."""
        ...

    def ping(self) -> bool:
        """Return true when the limiter backend is reachable."""
        ...


class RateLimitUnavailable(RuntimeError):
    """Raised when the selected distributed limiter cannot be reached."""


class InMemoryRateLimiter:
    """Local fixed-window-ish limiter used only for explicitly configured dev/test mode.

    Production must use Redis so limits survive restarts and coordinate across app
    instances. The production config validator rejects this backend.
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

    def ping(self) -> bool:
        """Return true for the in-process test/development limiter."""
        return True


class RedisRateLimiter:
    """Redis-backed fixed-window limiter for production-sensitive API surfaces."""

    def __init__(self, settings: Settings, *, client=None, clock=time.time) -> None:
        self.settings = settings
        self._client = client
        self._clock = clock

    @property
    def client(self):
        """Create a Redis client lazily."""
        if self._client is None:
            from redis import Redis

            self._client = Redis.from_url(
                self.settings.redis_url,
                socket_timeout=self.settings.rate_limit_redis_timeout_seconds,
                socket_connect_timeout=self.settings.rate_limit_redis_timeout_seconds,
                decode_responses=True,
            )
        return self._client

    def check(self, key: str, *, limit: int, window_seconds: int) -> RateLimitResult:
        """Increment a shared Redis bucket and return the rate-limit result."""
        if limit <= 0 or window_seconds <= 0:
            return RateLimitResult(allowed=True, retry_after_seconds=0)
        now = int(self._clock())
        bucket = now // window_seconds
        redis_key = f"{self.settings.rate_limit_redis_key_prefix}:{key}:{bucket}"
        retry_after = max(1, ((bucket + 1) * window_seconds) - now)
        try:
            count = int(self.client.incr(redis_key))
            if count == 1:
                self.client.expire(redis_key, window_seconds + 5)
        except Exception as exc:
            raise RateLimitUnavailable("Redis rate limiter unavailable") from exc
        if count > limit:
            return RateLimitResult(allowed=False, retry_after_seconds=retry_after)
        return RateLimitResult(allowed=True, retry_after_seconds=0)

    def ping(self) -> bool:
        """Return true when the Redis limiter backend is reachable."""
        try:
            return bool(self.client.ping())
        except Exception:
            return False


rate_limiter = InMemoryRateLimiter()
_redis_rate_limiters: dict[tuple[str, str, float], RedisRateLimiter] = {}


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
    limiter: RateLimiter | None = None,
    session: "Session | None" = None,
    tenant_id: str | None = None,
    tenant_id_resolver: Callable[[], str | None] | None = None,
    event_source: str | None = None,
    actor_category: str = "unknown",
) -> None:
    """Raise HTTP 429 when a request exceeds a configured policy."""
    if not settings.rate_limit_enabled:
        return
    window = window_seconds or settings.rate_limit_window_seconds
    identifier_values = [identifier for identifier in identifiers if identifier]
    request_client_ip = client_ip(request)
    key = rate_limit_key(scope, [request_client_ip, *identifier_values])
    selected_limiter = limiter or get_rate_limiter(settings)
    try:
        result = selected_limiter.check(key, limit=limit, window_seconds=window)
    except RateLimitUnavailable:
        logger.error("rate_limit_backend_unavailable", extra={"scope": scope})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiting is temporarily unavailable. Please try again shortly.",
            headers={"Retry-After": "5"},
        ) from None
    if result.allowed:
        return
    logger.warning(
        "rate_limit_exceeded",
        extra={"scope": scope, "retry_after_seconds": result.retry_after_seconds},
    )
    persist_rate_limit_exceeded(
        request,
        session=session,
        tenant_id=tenant_id,
        tenant_id_resolver=tenant_id_resolver,
        event_source=event_source,
        scope=scope,
        actor_category=actor_category,
        identifiers=identifier_values,
        limiter_key=key,
        limit=limit,
        window_seconds=window,
        retry_after_seconds=result.retry_after_seconds,
        request_client_ip=request_client_ip,
    )
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many requests. Please wait before trying again.",
        headers={"Retry-After": str(result.retry_after_seconds)},
    )


def persist_rate_limit_exceeded(
    request: Request,
    *,
    session: "Session | None",
    tenant_id: str | None,
    tenant_id_resolver: Callable[[], str | None] | None,
    event_source: str | None,
    scope: str,
    actor_category: str,
    identifiers: list[str],
    limiter_key: str,
    limit: int,
    window_seconds: int,
    retry_after_seconds: int,
    request_client_ip: str,
) -> None:
    """Best-effort durable abuse analytics for denied rate-limit requests."""
    if session is None:
        return
    resolved_tenant_id = tenant_id
    if resolved_tenant_id is None and tenant_id_resolver is not None:
        try:
            resolved_tenant_id = tenant_id_resolver()
        except Exception:
            logger.exception(
                "rate_limit_tenant_attribution_failed",
                extra={"scope": scope},
            )
            try:
                session.rollback()
            except Exception:
                logger.exception(
                    "rate_limit_tenant_attribution_rollback_failed",
                    extra={"scope": scope},
                )
    attributes = rate_limit_event_attributes(
        request,
        scope=scope,
        actor_category=actor_category,
        identifiers=identifiers,
        limiter_key=limiter_key,
        limit=limit,
        window_seconds=window_seconds,
        retry_after_seconds=retry_after_seconds,
        request_client_ip=request_client_ip,
    )
    try:
        from app.usage.service import UsageService

        UsageService(session).record_rate_limit_exceeded(
            tenant_id=resolved_tenant_id,
            event_source=event_source,
            attributes=attributes,
        )
        session.commit()
    except Exception:
        logger.exception(
            "rate_limit_analytics_persistence_failed",
            extra={"scope": scope, "tenant_attributed": bool(resolved_tenant_id)},
        )
        try:
            session.rollback()
        except Exception:
            logger.exception(
                "rate_limit_analytics_rollback_failed",
                extra={"scope": scope},
            )


def rate_limit_event_attributes(
    request: Request,
    *,
    scope: str,
    actor_category: str,
    identifiers: list[str],
    limiter_key: str,
    limit: int,
    window_seconds: int,
    retry_after_seconds: int,
    request_client_ip: str,
) -> dict[str, Any]:
    """Build a non-secret, analytics-safe rate-limit event payload."""
    attributes: dict[str, Any] = {
        "scope": scope,
        "actor_category": actor_category,
        "actor_fingerprint": fingerprint("|".join([request_client_ip, *identifiers])),
        "client_fingerprint": fingerprint(request_client_ip),
        "limiter_key_fingerprint": fingerprint(limiter_key),
        "identifier_count": len(identifiers),
        "limit": limit,
        "window_seconds": window_seconds,
        "retry_after_seconds": retry_after_seconds,
    }
    method = getattr(request, "method", None)
    if method:
        attributes["method"] = str(method).upper()[:12]
    route = safe_route_template(request)
    if route:
        attributes["route"] = route
    request_id = safe_request_id(request)
    if request_id:
        attributes["request_id"] = request_id
    return attributes


def safe_route_template(request: Request) -> str | None:
    """Return the FastAPI route template rather than the raw request path."""
    scope = getattr(request, "scope", None)
    if not isinstance(scope, dict):
        return None
    route = scope.get("route")
    path = getattr(route, "path", None)
    if not path:
        return None
    return str(path)[:160]


def safe_request_id(request: Request) -> str | None:
    """Return a bounded request/correlation id when it has a safe id shape."""
    headers = getattr(request, "headers", None)
    if headers is None:
        return None
    for header_name in REQUEST_ID_HEADERS:
        value = headers.get(header_name)
        if value and SAFE_REQUEST_ID_RE.fullmatch(value):
            return value
    return None


def get_rate_limiter(settings: Settings) -> RateLimiter:
    """Return the configured app-level rate limiter."""
    backend = settings.rate_limit_backend.strip().lower()
    if backend == "memory":
        return rate_limiter
    if backend == "redis":
        cache_key = (
            settings.redis_url,
            settings.rate_limit_redis_key_prefix,
            settings.rate_limit_redis_timeout_seconds,
        )
        if cache_key not in _redis_rate_limiters:
            _redis_rate_limiters[cache_key] = RedisRateLimiter(settings)
        return _redis_rate_limiters[cache_key]
    raise RateLimitUnavailable(f"Unsupported rate-limit backend: {backend}")


def rate_limit_readiness(settings: Settings) -> tuple[str, str]:
    """Return readiness status and detail for the configured limiter backend."""
    if not settings.rate_limit_enabled:
        return "disabled", "not_configured"
    backend = settings.rate_limit_backend.strip().lower()
    if backend == "memory":
        if settings.is_production():
            return "fail", "memory_backend_not_allowed_in_production"
        return "pass", "memory_dev_only"
    if backend != "redis":
        return "fail", "unsupported_backend"
    return ("pass", "redis") if get_rate_limiter(settings).ping() else ("fail", "redis_unavailable")
