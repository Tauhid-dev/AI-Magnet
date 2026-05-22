"""Signed session helpers for the MVP business portal."""

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
from app.models.tenant import BusinessUser, Tenant


@dataclass(frozen=True)
class BusinessPortalSession:
    """Authenticated business portal session context."""

    tenant_id: str
    tenant_name: str
    tenant_slug: str
    user_id: str
    email: str
    role: str


class BusinessPortalAuthService:
    """Issue and validate tenant-scoped business portal sessions."""

    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()

    def login(self, tenant_slug: str, email: str) -> tuple[str, BusinessPortalSession] | None:
        """Issue a signed session for an active business user."""
        statement = (
            select(Tenant, BusinessUser)
            .join(BusinessUser, BusinessUser.tenant_id == Tenant.id)
            .where(
                Tenant.slug == tenant_slug,
                Tenant.status == "active",
                func.lower(BusinessUser.email) == email.lower().strip(),
                BusinessUser.status == "active",
            )
        )
        row = self.session.execute(statement).first()
        if row is None:
            return None
        tenant, user = row
        session_context = BusinessPortalSession(
            tenant_id=tenant.id,
            tenant_name=tenant.name,
            tenant_slug=tenant.slug,
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
        return self.create_token(session_context), session_context

    def create_token(self, session_context: BusinessPortalSession) -> str:
        """Create an HMAC-signed bearer token."""
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.business_portal_session_ttl_minutes
        )
        payload = {
            "tenant_id": session_context.tenant_id,
            "tenant_name": session_context.tenant_name,
            "tenant_slug": session_context.tenant_slug,
            "user_id": session_context.user_id,
            "email": session_context.email,
            "role": session_context.role,
            "exp": int(expires_at.timestamp()),
        }
        encoded_payload = self._b64encode(json.dumps(payload, separators=(",", ":")).encode())
        signature = self._sign(encoded_payload)
        return f"{encoded_payload}.{signature}"

    def verify_token(self, token: str) -> BusinessPortalSession | None:
        """Verify a bearer token and return session context."""
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
        if not self._active_user_exists(payload):
            return None
        return BusinessPortalSession(
            tenant_id=payload["tenant_id"],
            tenant_name=payload["tenant_name"],
            tenant_slug=payload["tenant_slug"],
            user_id=payload["user_id"],
            email=payload["email"],
            role=payload["role"],
        )

    def _active_user_exists(self, payload: dict[str, Any]) -> bool:
        statement = (
            select(BusinessUser.id)
            .join(Tenant, Tenant.id == BusinessUser.tenant_id)
            .where(
                BusinessUser.id == payload.get("user_id"),
                BusinessUser.tenant_id == payload.get("tenant_id"),
                BusinessUser.email == payload.get("email"),
                BusinessUser.status == "active",
                Tenant.status == "active",
            )
        )
        return self.session.scalars(statement).first() is not None

    def _sign(self, encoded_payload: str) -> str:
        digest = hmac.new(
            self.settings.business_portal_session_secret.encode("utf-8"),
            encoded_payload.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return self._b64encode(digest)

    def _b64encode(self, value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    def _b64decode(self, value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)
