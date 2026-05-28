"""Audit helpers for security-sensitive admin actions."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.usage import AuditLog


class AuditService:
    """Write tenant-scoped audit records."""

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
            attributes=attributes or {},
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
            attributes=attributes or {},
        )
        self.session.add(audit_log)
        self.session.flush()
        return audit_log
