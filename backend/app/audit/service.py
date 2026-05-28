"""Audit helpers for security-sensitive admin actions."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.privacy import redact_mapping
from app.models.usage import AuditLog, GlobalAuditLog


class AuditService:
    """Write PII-safe tenant and platform audit records."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def record_admin_action(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        action: str,
        target_type: str,
        target_id: str,
        attributes: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Record a super admin action for a tenant-owned target."""
        audit_log = AuditLog(
            tenant_id=tenant_id,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            attributes=redact_mapping(attributes),
        )
        self.session.add(audit_log)
        self.session.flush()
        return audit_log

    def record_business_action(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        action: str,
        target_type: str,
        target_id: str,
        attributes: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Record a business portal action for a tenant-owned actor/target."""
        audit_log = AuditLog(
            tenant_id=tenant_id,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            attributes=redact_mapping(attributes),
        )
        self.session.add(audit_log)
        self.session.flush()
        return audit_log

    def record_global_admin_action(
        self,
        *,
        actor_id: str | None,
        action: str,
        target_type: str | None = None,
        target_id: str | None = None,
        tenant_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> GlobalAuditLog:
        """Record a platform-level admin action that survives tenant deletion."""
        audit_log = GlobalAuditLog(
            tenant_id=tenant_id,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            attributes=redact_mapping(attributes),
        )
        self.session.add(audit_log)
        self.session.flush()
        return audit_log
