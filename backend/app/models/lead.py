"""Lead capture models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class Lead(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Structured lead captured from chat or future channels."""

    __tablename__ = "leads"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_leads_tenant_id_id"),
        ForeignKeyConstraint(
            ["tenant_id", "conversation_id"],
            ["conversations.tenant_id", "conversations.id"],
            name="fk_leads_conversation_same_tenant",
        ),
    )

    conversation_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    job_type: Mapped[str | None] = mapped_column(String(160), nullable=True)
    suburb: Mapped[str | None] = mapped_column(String(160), nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(60), nullable=False, default="new", index=True)
    qualified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    qualification_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notification_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="not_queued",
        index=True,
    )
    last_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
