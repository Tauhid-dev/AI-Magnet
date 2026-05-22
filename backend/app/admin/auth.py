"""Signed session helpers for the super admin portal."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.admin import AdminUser


SUPER_ADMIN_ROLES = {"super_admin"}


@dataclass(frozen=True)
class AdminPortalSession:
    """Authenticated super admin session context."""

    admin_id: str
    email: str
    full_name: str | None
    role: str


class AdminPortalAuthService:
    """Issue and validate global super admin portal sessions."""

    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()

    def login(self, email: str) -> tuple[str, AdminPortalSession] | None:
        """Issue a signed session for an active super admin."""
        statement = select(AdminUser).where(
            func.lower(AdminUser.email) == email.lower().strip(),
            AdminUser.status == "active",
            AdminUser.role.in_(SUPER_ADMIN_ROLES),
        )
        admin = self.session.scalars(statement).first()
        if admin is None:
            return None
        session_context = AdminPortalSession(
            admin_id=admin.id,
            email=admin.email,
            full_name=admin.full_name,
            role=admin.role,
        )
        return self.create_token(session_context), session_context

    def create_token(self, session_context: AdminPortalSession) -> str:
        """Create an HMAC-signed admin bearer token."""
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.admin_portal_session_ttl_minutes
        )
        payload = {
            "admin_id": session_context.admin_id,
            "email": session_context.email,
            "full_name": session_context.full_name,
            "role": session_context.role,
            "exp": int(expires_at.timestamp()),
        }
        encoded_payload = self._b64encode(json.dumps(payload, separators=(",", ":")).encode())
        signature = self._sign(encoded_payload)
        return f"{encoded_payload}.{signature}"

    def verify_token(self, token: str) -> AdminPortalSession | None:
        """Verify an admin bearer token and return session context."""
        try:
            encoded_payload, signature = token.split(".", 1)
        except ValueError:
            return None
        expected_signature = self._sign(encoded_payload)
        if not hmac.compare_digest(signature, expected_signature):
            return None
        try:
            payload = json.loads(self._b64decode(encoded_payload))
        except (ValueError, json.JSONDecodeError):
            return None
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            return None
        admin = self._active_admin(payload)
        if admin is None:
            return None
        return AdminPortalSession(
            admin_id=admin.id,
            email=admin.email,
            full_name=admin.full_name,
            role=admin.role,
        )

    def _active_admin(self, payload: dict[str, Any]) -> AdminUser | None:
        statement = select(AdminUser).where(
            AdminUser.id == payload.get("admin_id"),
            AdminUser.email == payload.get("email"),
            AdminUser.status == "active",
            AdminUser.role.in_(SUPER_ADMIN_ROLES),
        )
        return self.session.scalars(statement).first()

    def _sign(self, encoded_payload: str) -> str:
        digest = hmac.new(
            self.settings.admin_portal_session_secret.encode("utf-8"),
            encoded_payload.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return self._b64encode(digest)

    def _b64encode(self, value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    def _b64decode(self, value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)
