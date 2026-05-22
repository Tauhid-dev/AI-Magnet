"""Safe local-development seed helpers."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.tenants.service import TenantService


def seed_local_development_data(session: Session) -> None:
    """Create one local demo tenant if no tenants exist.

    This helper is intentionally not called automatically. Future phases can wire it
    into explicit local setup commands without seeding production data.
    """
    tenant_service = TenantService(session)
    if tenant_service.list_tenants():
        return

    tenant = tenant_service.create_tenant(name="Demo Tradie Co", slug="demo-tradie")
    tenant_service.create_business(
        tenant_id=tenant.id,
        name="Demo Tradie Co",
        email="owner@example.test",
    )
