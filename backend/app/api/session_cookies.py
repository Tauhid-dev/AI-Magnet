"""Shared helpers for HttpOnly portal session cookies."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, Request, Response, status

from app.core.config import Settings


CSRF_HEADER_NAME = "X-AI-Magnet-CSRF"
UNSAFE_METHODS = {"POST", "PATCH", "PUT", "DELETE"}


@dataclass(frozen=True)
class SessionToken:
    """Resolved portal session token and transport source."""

    token: str
    source: str


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
    resolved = get_session_token_with_source(
        request,
        authorization,
        cookie_name=cookie_name,
    )
    return resolved.token if resolved else None


def get_session_token_with_source(
    request: Request,
    authorization: str | None,
    *,
    cookie_name: str,
) -> SessionToken | None:
    """Resolve a token and identify whether it came from bearer auth or a cookie."""
    if authorization and authorization.lower().startswith("bearer "):
        return SessionToken(token=authorization.split(" ", 1)[1], source="authorization")
    cookie_token = request.cookies.get(cookie_name)
    if cookie_token:
        return SessionToken(token=cookie_token, source="cookie")
    return None


def require_csrf_header_for_cookie_session(
    request: Request,
    resolved_token: SessionToken,
) -> None:
    """Require a custom header for unsafe cookie-authenticated portal requests."""
    if resolved_token.source != "cookie" or request.method.upper() not in UNSAFE_METHODS:
        return
    if request.headers.get(CSRF_HEADER_NAME) == "1":
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Missing CSRF confirmation header",
    )


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
