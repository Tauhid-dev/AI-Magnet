"""Global platform admin models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TimestampMixin


class AdminUser(IdMixin, TimestampMixin, Base):
    """Global super admin user, separate from tenant business users."""

    __tablename__ = "admin_users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(60), nullable=False, default="super_admin", index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active", index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    session_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    mfa_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
