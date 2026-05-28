"""Shared helpers for HttpOnly portal session cookies."""

from __future__ import annotations

from fastapi import Request, Response

from app.core.config import Settings


def session_cookie_secure(settings: Settings) -> bool:
    """Force secure cookies in production while allowing local HTTP development."""
    return settings.auth_cookie_secure or settings.environment.strip().lower() in {
        "prod",
        "production",
    }


def get_session_token(
    request: Request,
    authorization: str | None,
    *,
    cookie_name: str,
) -> str | None:
    """Resolve a session token from explicit bearer header first, then cookie."""
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    cookie_token = request.cookies.get(cookie_name)
    if cookie_token:
        return cookie_token
    return None


def set_session_cookie(
    response: Response,
    *,
    name: str,
    token: str,
    max_age_seconds: int,
    settings: Settings,
) -> None:
    """Attach a secure HttpOnly session cookie to a response."""
    response.set_cookie(
        key=name,
        value=token,
        max_age=max_age_seconds,
        httponly=True,
        secure=session_cookie_secure(settings),
        samesite=settings.auth_cookie_samesite,
    )


def clear_session_cookie(
    response: Response,
    *,
    name: str,
    settings: Settings,
) -> None:
    """Clear a portal session cookie."""
    response.delete_cookie(
        key=name,
        httponly=True,
        secure=session_cookie_secure(settings),
        samesite=settings.auth_cookie_samesite,
    )
