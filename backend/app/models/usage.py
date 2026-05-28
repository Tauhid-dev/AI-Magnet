"""Usage and audit log models."""

from __future__ import annotations

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class UsageLog(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Tenant-scoped usage event for analytics and future billing."""

    __tablename__ = "usage_logs"

    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    event_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class AuditLog(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Tenant-scoped audit event for security-sensitive actions."""

    __tablename__ = "audit_logs"

    actor_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class GlobalAuditLog(IdMixin, TimestampMixin, Base):
    """Platform-level audit event that survives tenant deletion/offboarding."""

    __tablename__ = "global_audit_logs"

    tenant_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    actor_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
