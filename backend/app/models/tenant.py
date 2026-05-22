"""Tenant and business account models."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class Tenant(IdMixin, TimestampMixin, Base):
    """Top-level tenant for one tradie/local business customer."""

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active", index=True)

    businesses: Mapped[list[Business]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan",
    )


class Business(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Business profile owned by a tenant."""

    __tablename__ = "businesses"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_business_tenant_name"),)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    tenant: Mapped[Tenant] = relationship(back_populates="businesses")


class BusinessUser(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Tenant-scoped user account placeholder for business portal access."""

    __tablename__ = "business_users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_business_user_tenant_email"),)

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(60), nullable=False, default="owner")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    business_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("businesses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
