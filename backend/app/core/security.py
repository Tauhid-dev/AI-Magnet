"""Security helpers for HTTP responses and runtime guardrails."""

from __future__ import annotations

from collections.abc import MutableMapping


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": (
        "default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'"
    ),
}


def apply_security_headers(headers: MutableMapping[str, str]) -> None:
    """Set conservative security headers without overriding explicit values."""
    for header, value in SECURITY_HEADERS.items():
        headers.setdefault(header, value)
