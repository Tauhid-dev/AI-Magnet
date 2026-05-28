"""Tenant-safe website widget key resolution."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.widget import WidgetConfig


WIDGET_KEY_PREFIX = "wm_live_"
WIDGET_TERMINAL_STATUSES = {"revoked", "rotated"}
WIDGET_ALLOWED_MUTABLE_STATUSES = {"active", "disabled"}


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

    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()

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
        serialized_origins = self._serialize_origins(allowed_origins)
        if self.settings.widget_require_allowed_origins and not serialized_origins:
            raise ValueError("At least one allowed origin is required for widget keys")
        widget = WidgetConfig(
            tenant_id=tenant_id,
            widget_key_hash=hash_widget_key(widget_key),
            key_prefix=widget_key_prefix(widget_key),
            name=name,
            status="active",
            allowed_origins=serialized_origins,
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
        return self._set_widget_status(widget_id, tenant_id, "revoked")

    def disable_widget(self, widget_id: str, tenant_id: str) -> WidgetConfig | None:
        """Mark a tenant-owned widget as disabled without destroying its history."""
        return self._set_widget_status(widget_id, tenant_id, "disabled")

    def update_allowed_origins(
        self,
        widget_id: str,
        tenant_id: str,
        allowed_origins: list[str],
    ) -> WidgetConfig | None:
        """Replace allowed browser origins for a tenant-owned widget."""
        widget = self._get_widget(widget_id, tenant_id)
        if widget is None or widget.status in WIDGET_TERMINAL_STATUSES:
            return None
        serialized_origins = self._serialize_origins(allowed_origins)
        if self.settings.widget_require_allowed_origins and not serialized_origins:
            raise ValueError("At least one allowed origin is required for widget keys")
        widget.allowed_origins = serialized_origins
        self.session.flush()
        return widget

    def update_branding(
        self,
        widget_id: str,
        tenant_id: str,
        *,
        name: str,
    ) -> WidgetConfig | None:
        """Update beta-scope widget display branding for a tenant-owned widget."""
        widget = self._get_widget(widget_id, tenant_id)
        if widget is None or widget.status in WIDGET_TERMINAL_STATUSES:
            return None
        widget.name = name.strip()
        self.session.flush()
        return widget

    def rotate_widget(
        self,
        widget_id: str,
        tenant_id: str,
        *,
        new_widget_key: str,
        allowed_origins: list[str] | None = None,
    ) -> WidgetConfig | None:
        """Revoke the old widget key and create a replacement key."""
        widget = self._get_widget(widget_id, tenant_id)
        if widget is None or widget.status in WIDGET_TERMINAL_STATUSES:
            return None
        serialized_origins = (
            self._serialize_origins(allowed_origins)
            if allowed_origins is not None
            else widget.allowed_origins
        )
        if self.settings.widget_require_allowed_origins and not serialized_origins:
            raise ValueError("At least one allowed origin is required for widget keys")
        widget.status = "rotated"
        replacement = WidgetConfig(
            tenant_id=tenant_id,
            widget_key_hash=hash_widget_key(new_widget_key),
            key_prefix=widget_key_prefix(new_widget_key),
            name=widget.name,
            status="active",
            allowed_origins=serialized_origins,
        )
        self.session.add(replacement)
        self.session.flush()
        return replacement

    def parsed_allowed_origins(self, widget: WidgetConfig) -> list[str]:
        """Return normalized origins for API responses."""
        if not widget.allowed_origins:
            return []
        return [
            origin.strip()
            for origin in widget.allowed_origins.splitlines()
            if origin.strip()
        ]

    def _get_widget(self, widget_id: str, tenant_id: str) -> WidgetConfig | None:
        statement = select(WidgetConfig).where(
            WidgetConfig.id == widget_id,
            WidgetConfig.tenant_id == tenant_id,
        )
        return self.session.scalars(statement).first()

    def _set_widget_status(
        self,
        widget_id: str,
        tenant_id: str,
        new_status: str,
    ) -> WidgetConfig | None:
        widget = self._get_widget(widget_id, tenant_id)
        if widget is None:
            return None
        if (
            new_status not in WIDGET_ALLOWED_MUTABLE_STATUSES
            and new_status not in WIDGET_TERMINAL_STATUSES
        ):
            raise ValueError("Unsupported widget status")
        widget.status = new_status
        self.session.flush()
        return widget

    def _serialize_origins(self, origins: list[str] | None) -> str | None:
        if not origins:
            return None
        normalized = sorted({normalize_origin(origin) for origin in origins if origin.strip()})
        if len(normalized) > 20:
            raise ValueError("A widget key can have at most 20 allowed origins")
        return "\n".join(normalized) if normalized else None

    def _origin_allowed(self, allowed_origins: str | None, request_origin: str | None) -> bool:
        if not allowed_origins:
            return not self.settings.widget_require_allowed_origins
        if not request_origin:
            return False
        try:
            normalized_request_origin = normalize_origin(request_origin)
        except ValueError:
            return False
        allowed = {origin.strip().lower() for origin in allowed_origins.splitlines()}
        return normalized_request_origin.lower() in allowed


def normalize_origin(origin: str) -> str:
    """Normalize browser origin strings and reject path/query wildcards."""
    parsed = urlparse(origin.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.hostname is None:
        raise ValueError("Allowed origins must be absolute http(s) origins")
    if parsed.path not in {"", "/"} or parsed.params or parsed.query or parsed.fragment:
        raise ValueError("Allowed origins must not include path, query, or fragment")
    hostname = parsed.hostname.lower()
    try:
        port_value = parsed.port
    except ValueError as exc:
        raise ValueError("Allowed origins must include a valid port") from exc
    port = f":{port_value}" if port_value else ""
    return f"{parsed.scheme.lower()}://{hostname}{port}"
