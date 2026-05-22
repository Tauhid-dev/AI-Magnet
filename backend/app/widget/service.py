"""Tenant-safe website widget key resolution."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.widget import WidgetConfig


WIDGET_KEY_PREFIX = "wm_live_"


def hash_widget_key(widget_key: str) -> str:
    """Hash a public widget key before database lookup/storage."""
    return hashlib.sha256(widget_key.encode("utf-8")).hexdigest()


def widget_key_prefix(widget_key: str) -> str:
    """Return a short non-secret prefix for support and diagnostics."""
    return widget_key[: min(len(widget_key), 16)]


@dataclass(frozen=True)
class WidgetResolution:
    """Resolved widget key and tenant context."""

    widget: WidgetConfig
    tenant_id: str


class WidgetService:
    """Manage and resolve public widget keys."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def generate_widget_key(self) -> str:
        """Generate a browser-safe public widget key."""
        return f"{WIDGET_KEY_PREFIX}{secrets.token_urlsafe(24)}"

    def create_widget_config(
        self,
        tenant_id: str,
        widget_key: str,
        name: str = "Website widget",
        allowed_origins: list[str] | None = None,
    ) -> WidgetConfig:
        """Create an active widget config without storing the raw key."""
        widget = WidgetConfig(
            tenant_id=tenant_id,
            widget_key_hash=hash_widget_key(widget_key),
            key_prefix=widget_key_prefix(widget_key),
            name=name,
            status="active",
            allowed_origins=self._serialize_origins(allowed_origins),
        )
        self.session.add(widget)
        self.session.flush()
        return widget

    def resolve_widget_key(
        self,
        widget_key: str,
        request_origin: str | None = None,
    ) -> WidgetResolution | None:
        """Resolve an active public widget key to exactly one tenant."""
        statement = select(WidgetConfig).where(
            WidgetConfig.widget_key_hash == hash_widget_key(widget_key),
            WidgetConfig.status == "active",
        )
        widget = self.session.scalars(statement).first()
        if widget is None:
            return None
        if not self._origin_allowed(widget.allowed_origins, request_origin):
            return None
        return WidgetResolution(widget=widget, tenant_id=widget.tenant_id)

    def revoke_widget(self, widget_id: str, tenant_id: str) -> WidgetConfig | None:
        """Mark a tenant-owned widget as revoked."""
        statement = select(WidgetConfig).where(
            WidgetConfig.id == widget_id,
            WidgetConfig.tenant_id == tenant_id,
        )
        widget = self.session.scalars(statement).first()
        if widget is None:
            return None
        widget.status = "revoked"
        self.session.flush()
        return widget

    def _serialize_origins(self, origins: list[str] | None) -> str | None:
        if not origins:
            return None
        return "\n".join(sorted({origin.strip() for origin in origins if origin.strip()}))

    def _origin_allowed(self, allowed_origins: str | None, request_origin: str | None) -> bool:
        if not allowed_origins:
            return True
        if not request_origin:
            return False
        allowed = {origin.strip().lower() for origin in allowed_origins.splitlines()}
        return request_origin.strip().lower() in allowed
