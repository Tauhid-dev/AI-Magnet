from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.config import Settings
from app.core.rate_limit import (
    InMemoryRateLimiter,
    RedisRateLimiter,
    RateLimitUnavailable,
    enforce_rate_limit,
    get_rate_limiter,
    rate_limit_readiness,
    rate_limiter,
)


class FakeRedis:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.store: dict[str, int] = {}
        self.expiry: dict[str, int] = {}

    def incr(self, key: str) -> int:
        if self.fail:
            raise RuntimeError("redis unavailable")
        self.store[key] = self.store.get(key, 0) + 1
        return self.store[key]

    def expire(self, key: str, seconds: int) -> bool:
        if self.fail:
            raise RuntimeError("redis unavailable")
        self.expiry[key] = seconds
        return True

    def ping(self) -> bool:
        return not self.fail


def fake_request(host: str = "198.51.100.10"):
    return SimpleNamespace(client=SimpleNamespace(host=host))


def test_limiter_selection_is_explicit_for_dev_and_production():
    memory_settings = Settings(rate_limit_backend="memory")
    redis_settings = Settings(
        environment="production",
        rate_limit_backend="redis",
        redis_url="redis://redis:6379/0",
    )

    assert get_rate_limiter(memory_settings) is rate_limiter
    assert isinstance(get_rate_limiter(redis_settings), RedisRateLimiter)


def test_memory_limiter_rejection_includes_retry_header():
    limiter = InMemoryRateLimiter()
    settings = Settings(
        rate_limit_backend="memory",
        rate_limit_window_seconds=60,
    )

    enforce_rate_limit(
        fake_request(),
        settings,
        scope="test",
        identifiers=["subject"],
        limit=1,
        limiter=limiter,
    )
    with pytest.raises(HTTPException) as exc:
        enforce_rate_limit(
            fake_request(),
            settings,
            scope="test",
            identifiers=["subject"],
            limit=1,
            limiter=limiter,
        )

    assert exc.value.status_code == 429
    assert int(exc.value.headers["Retry-After"]) > 0


def test_redis_limiter_coordinates_counts_and_retry_window():
    redis = FakeRedis()
    settings = Settings(
        environment="production",
        rate_limit_backend="redis",
        redis_url="redis://redis:6379/0",
        rate_limit_redis_key_prefix="test-rate-limit",
    )
    limiter = RedisRateLimiter(settings, client=redis, clock=lambda: 120)

    first = limiter.check("admin_login:test", limit=1, window_seconds=60)
    second = limiter.check("admin_login:test", limit=1, window_seconds=60)

    assert first.allowed is True
    assert second.allowed is False
    assert second.retry_after_seconds == 60
    assert list(redis.store.values()) == [2]
    assert list(redis.expiry.values()) == [65]


def test_production_redis_limiter_failure_fails_closed_with_503():
    settings = Settings(
        environment="production",
        rate_limit_backend="redis",
        redis_url="redis://redis:6379/0",
    )
    limiter = RedisRateLimiter(settings, client=FakeRedis(fail=True))

    with pytest.raises(HTTPException) as exc:
        enforce_rate_limit(
            fake_request(),
            settings,
            scope="admin_login",
            identifiers=["admin@example.test"],
            limit=1,
            limiter=limiter,
        )

    assert exc.value.status_code == 503
    assert exc.value.headers["Retry-After"] == "5"


def test_redis_limiter_exposes_readiness_failure():
    settings = Settings(
        environment="production",
        rate_limit_backend="redis",
        redis_url="redis://redis:6379/0",
    )
    limiter = RedisRateLimiter(settings, client=FakeRedis(fail=True))

    assert limiter.ping() is False
    with pytest.raises(RateLimitUnavailable):
        limiter.check("admin_login:test", limit=1, window_seconds=60)
    assert rate_limit_readiness(Settings(rate_limit_backend="memory")) == (
        "pass",
        "memory_dev_only",
    )
