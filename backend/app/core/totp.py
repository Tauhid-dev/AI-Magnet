"""Small RFC 6238 TOTP verifier for admin MFA."""

from __future__ import annotations

import base64
import hashlib
import hmac
import struct
import time


def verify_totp_code(
    secret: str | None,
    code: str | None,
    *,
    timestamp: int | None = None,
    step_seconds: int = 30,
    window: int = 1,
) -> bool:
    """Validate a six-digit TOTP code with a small clock-skew window."""
    if not secret or not code:
        return False
    normalized_code = "".join(character for character in code if character.isdigit())
    if len(normalized_code) != 6:
        return False
    current_counter = int((timestamp if timestamp is not None else time.time()) // step_seconds)
    for offset in range(-window, window + 1):
        expected = generate_totp_code(secret, current_counter + offset)
        if hmac.compare_digest(expected, normalized_code):
            return True
    return False


def generate_totp_code(secret: str, counter: int) -> str:
    """Generate a six-digit TOTP code for tests and verification."""
    key = _decode_secret(secret)
    message = struct.pack(">Q", counter)
    digest = hmac.new(key, message, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}"


def _decode_secret(secret: str) -> bytes:
    normalized = secret.strip().replace(" ", "").upper()
    padding = "=" * (-len(normalized) % 8)
    return base64.b32decode(normalized + padding, casefold=True)
