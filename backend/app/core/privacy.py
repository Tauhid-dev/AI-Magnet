"""Privacy helpers for PII-safe logs and audit attributes."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any


PII_KEY_MARKERS = (
    "email",
    "phone",
    "mobile",
    "customer_name",
    "full_name",
    "password",
    "secret",
    "token",
    "body_text",
    "content",
    "message",
)


def stable_hash(value: str) -> str:
    """Return a short stable hash for correlation without storing raw PII."""
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()[:24]


def is_pii_key(key: str) -> bool:
    """Return true when an attribute key is likely to contain PII or secrets."""
    normalized_key = key.strip().lower()
    return any(marker in normalized_key for marker in PII_KEY_MARKERS)


def redact_value(value: Any) -> dict[str, Any]:
    """Redact a value while preserving enough metadata for audit correlation."""
    if value is None:
        return {"redacted": True}
    value_text = str(value)
    payload: dict[str, Any] = {"redacted": True, "length": len(value_text)}
    if value_text:
        payload["sha256"] = stable_hash(value_text)
    return payload


def redact_mapping(attributes: Mapping[str, Any] | None) -> dict[str, Any]:
    """Recursively redact likely PII from audit/log attributes."""
    if not attributes:
        return {}
    redacted: dict[str, Any] = {}
    for key, value in attributes.items():
        if is_pii_key(key):
            redacted[key] = redact_value(value)
        elif isinstance(value, Mapping):
            redacted[key] = redact_mapping(value)
        elif isinstance(value, list):
            redacted[key] = [
                redact_mapping(item) if isinstance(item, Mapping) else item for item in value
            ]
        else:
            redacted[key] = value
    return redacted
