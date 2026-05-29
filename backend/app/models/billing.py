"""Tenant subscription and entitlement models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class TenantSubscription(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Manual paid-beta subscription and entitlement state for one tenant."""

    __tablename__ = "tenant_subscriptions"
    __table_args__ = (
        UniqueConstraint("tenant_id", name="uq_tenant_subscriptions_tenant_id"),
    )

    plan_code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    plan_name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    billing_mode: Mapped[str] = mapped_column(String(40), nullable=False, default="manual")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="AUD")
    monthly_price_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    support_level: Mapped[str] = mapped_column(String(80), nullable=False, default="standard")

    chat_conversations_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    ai_responses_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_budget_cents: Mapped[float] = mapped_column(Float, nullable=False)
    documents_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_mb_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    pages_crawled_limit: Mapped[int] = mapped_column(Integer, nullable=False)

    trial_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    billing_contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manual_reference: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_by_admin_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )
