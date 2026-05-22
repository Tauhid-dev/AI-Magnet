"""Lead capture models."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class Lead(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Structured lead captured from chat or future channels."""

    __tablename__ = "leads"

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
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
