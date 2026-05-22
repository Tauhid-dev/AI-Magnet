"""Global platform admin models."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TimestampMixin


class AdminUser(IdMixin, TimestampMixin, Base):
    """Global super admin user, separate from tenant business users."""

    __tablename__ = "admin_users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(60), nullable=False, default="super_admin", index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active", index=True)
