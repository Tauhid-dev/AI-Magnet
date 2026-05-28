"""Safe local-development seed helpers."""

from __future__ import annotations

import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.passwords import hash_password
from app.db.base import utc_now
from app.models.admin import AdminUser
from app.models.tenant import BusinessUser
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
                password_hash=hash_password(
                    os.getenv("LOCAL_DEV_ADMIN_PASSWORD", "local-admin-password")
                ),
                password_updated_at=utc_now(),
                mfa_required=False,
            )
        )
        session.flush()

    tenant_service = TenantService(session)
    if tenant_service.list_tenants():
        return

    tenant = tenant_service.create_tenant(name="Demo Tradie Co", slug="demo-tradie")
    business = tenant_service.create_business(
        tenant_id=tenant.id,
        name="Demo Tradie Co",
        email="owner@example.test",
    )
    session.add(
        BusinessUser(
            tenant_id=tenant.id,
            business_id=business.id,
            email="owner@example.test",
            full_name="Demo Owner",
            role="owner",
            status="active",
            password_hash=hash_password(
                os.getenv("LOCAL_DEV_BUSINESS_PASSWORD", "local-business-password")
            ),
            password_updated_at=utc_now(),
        )
    )
