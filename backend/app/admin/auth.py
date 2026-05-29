"""Password-authenticated session helpers for the super admin portal."""

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
from app.core.passwords import verify_password
from app.core.totp import is_totp_secret_configured, verify_totp_code
from app.models.admin import AdminUser


SUPER_ADMIN_ROLES = {"super_admin"}


@dataclass(frozen=True)
class AdminPortalSession:
    """Authenticated super admin session context."""

    admin_id: str
    email: str
    full_name: str | None
    role: str
    session_version: int


class AdminPortalAuthService:
    """Issue and validate global super admin portal sessions."""

    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()

    def login(
        self,
        email: str,
        password: str,
        mfa_code: str | None = None,
    ) -> tuple[str, AdminPortalSession] | None:
        """Issue a signed session for an active super admin with password and MFA."""
        statement = select(AdminUser).where(
            func.lower(AdminUser.email) == email.lower().strip(),
            AdminUser.status == "active",
            AdminUser.role.in_(SUPER_ADMIN_ROLES),
        )
        admin = self.session.scalars(statement).first()
        if admin is None:
            return None
        if self._is_locked(admin.locked_until):
            return None
        if not verify_password(password, admin.password_hash):
            self._register_failed_login(admin)
            return None
        if not self._admin_has_required_mfa(admin):
            self._register_failed_login(admin)
            return None
        if self._admin_requires_mfa(admin) and not verify_totp_code(
            admin.mfa_secret,
            mfa_code,
        ):
            self._register_failed_login(admin)
            return None
        self._register_successful_login(admin)
        session_context = AdminPortalSession(
            admin_id=admin.id,
            email=admin.email,
            full_name=admin.full_name,
            role=admin.role,
            session_version=admin.session_version,
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
            "session_version": session_context.session_version,
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
            session_version=admin.session_version,
        )

    def revoke_sessions(self, admin_id: str) -> bool:
        """Revoke all sessions for an admin by bumping the token version."""
        admin = self.session.get(AdminUser, admin_id)
        if admin is None:
            return False
        admin.session_version += 1
        self.session.flush()
        return True

    def _active_admin(self, payload: dict[str, Any]) -> AdminUser | None:
        statement = select(AdminUser).where(
            AdminUser.id == payload.get("admin_id"),
            AdminUser.email == payload.get("email"),
            AdminUser.status == "active",
            AdminUser.role.in_(SUPER_ADMIN_ROLES),
        )
        admin = self.session.scalars(statement).first()
        if admin is None:
            return None
        try:
            token_session_version = int(payload["session_version"])
        except (KeyError, TypeError, ValueError):
            return None
        if admin.session_version != token_session_version:
            return None
        if not self._admin_has_required_mfa(admin):
            return None
        return admin

    def production_super_admin_mfa_issue_count(self) -> int:
        """Count active super admins that would be blocked by production MFA rules."""
        if not self.settings.is_production():
            return 0
        statement = select(AdminUser).where(
            AdminUser.status == "active",
            AdminUser.role.in_(SUPER_ADMIN_ROLES),
        )
        return sum(
            1
            for admin in self.session.scalars(statement).all()
            if not self._admin_has_required_mfa(admin)
        )

    def _admin_requires_mfa(self, admin: AdminUser) -> bool:
        """Return whether the admin must provide MFA for the current environment."""
        if self.settings.is_production() and admin.role in SUPER_ADMIN_ROLES:
            return True
        return bool(admin.mfa_required)

    def _admin_has_required_mfa(self, admin: AdminUser) -> bool:
        """Return true when required MFA is enabled and has a configured secret."""
        if not self._admin_requires_mfa(admin):
            return True
        return bool(admin.mfa_required and is_totp_secret_configured(admin.mfa_secret))

    def _register_failed_login(self, admin: AdminUser) -> None:
        admin.failed_login_count += 1
        if admin.failed_login_count >= self.settings.auth_failed_login_limit:
            admin.locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=self.settings.auth_lockout_minutes
            )
        self.session.flush()

    def _register_successful_login(self, admin: AdminUser) -> None:
        admin.failed_login_count = 0
        admin.locked_until = None
        admin.last_login_at = datetime.now(timezone.utc)
        self.session.flush()

    def _is_locked(self, locked_until: datetime | None) -> bool:
        if locked_until is None:
            return False
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)
        return locked_until > datetime.now(timezone.utc)

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
