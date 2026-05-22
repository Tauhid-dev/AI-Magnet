"""Tenant and business service helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant import Business, Tenant


class TenantService:
    """Internal service for basic tenant and business CRUD."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_tenant(self, name: str, slug: str, status: str = "active") -> Tenant:
        tenant = Tenant(name=name, slug=slug, status=status)
        self.session.add(tenant)
        self.session.flush()
        return tenant

    def get_tenant(self, tenant_id: str) -> Tenant | None:
        return self.session.get(Tenant, tenant_id)

    def list_tenants(self) -> list[Tenant]:
        return list(self.session.scalars(select(Tenant).order_by(Tenant.created_at)))

    def create_business(
        self,
        tenant_id: str,
        name: str,
        email: str | None = None,
        phone: str | None = None,
        website_url: str | None = None,
    ) -> Business:
        business = Business(
            tenant_id=tenant_id,
            name=name,
            email=email,
            phone=phone,
            website_url=website_url,
        )
        self.session.add(business)
        self.session.flush()
        return business

    def list_businesses(self, tenant_id: str) -> list[Business]:
        statement = (
            select(Business)
            .where(Business.tenant_id == tenant_id)
            .order_by(Business.created_at)
        )
        return list(self.session.scalars(statement))
