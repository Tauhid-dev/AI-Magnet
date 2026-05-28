"""Password hashing helpers built on the Python standard library."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets


ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 260_000
SALT_BYTES = 16


def hash_password(password: str, *, iterations: int = DEFAULT_ITERATIONS) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256."""
    if not password:
        raise ValueError("Password must not be empty")
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "$".join(
        [
            ALGORITHM,
            str(iterations),
            _b64encode(salt),
            _b64encode(digest),
        ]
    )


def verify_password(password: str, password_hash: str | None) -> bool:
    """Return true when password matches the stored hash."""
    if not password or not password_hash:
        return False
    try:
        algorithm, iterations_text, salt_text, digest_text = password_hash.split("$", 3)
        if algorithm != ALGORITHM:
            return False
        iterations = int(iterations_text)
        salt = _b64decode(salt_text)
        expected = _b64decode(digest_text)
    except (ValueError, TypeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
