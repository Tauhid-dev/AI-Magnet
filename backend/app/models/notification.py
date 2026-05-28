"""Tenant-scoped notification models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class BusinessNotificationSetting(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Tenant-level notification preferences for lead alerts."""

    __tablename__ = "business_notification_settings"
    __table_args__ = (
        UniqueConstraint("tenant_id", name="uq_business_notification_settings_tenant"),
        ForeignKeyConstraint(
            ["tenant_id", "business_id"],
            ["businesses.tenant_id", "businesses.id"],
            name="fk_notification_settings_business_same_tenant",
        ),
    )

    business_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("businesses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    notification_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lead_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


class NotificationDelivery(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Delivery attempt state for tenant-owned notifications."""

    __tablename__ = "notification_deliveries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "lead_id"],
            ["leads.tenant_id", "leads.id"],
            name="fk_notification_deliveries_lead_same_tenant",
        ),
    )

    lead_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    notification_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="queued", index=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
