"""Widget configuration models."""

from __future__ import annotations

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class WidgetConfig(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Public website widget configuration mapped to one tenant."""

    __tablename__ = "widget_configs"
    __table_args__ = (
        UniqueConstraint("widget_key_hash", name="uq_widget_configs_key_hash"),
    )

    widget_key_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    key_prefix: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, default="Website widget")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active", index=True)
    allowed_origins: Mapped[str | None] = mapped_column(Text, nullable=True)
