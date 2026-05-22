"""Safe local-development seed helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admin import AdminUser
from app.tenants.service import TenantService


def seed_local_development_data(session: Session) -> None:
    """Create safe local demo records if they do not exist.

    This helper is intentionally not called automatically. Future phases can wire it
    into explicit local setup commands without seeding production data.
    """
    if session.scalars(select(AdminUser.id)).first() is None:
        session.add(
            AdminUser(
                email="admin@example.test",
                full_name="Local Platform Admin",
                role="super_admin",
                status="active",
            )
        )
        session.flush()

    tenant_service = TenantService(session)
    if tenant_service.list_tenants():
        return

    tenant = tenant_service.create_tenant(name="Demo Tradie Co", slug="demo-tradie")
    tenant_service.create_business(
        tenant_id=tenant.id,
        name="Demo Tradie Co",
        email="owner@example.test",
    )
