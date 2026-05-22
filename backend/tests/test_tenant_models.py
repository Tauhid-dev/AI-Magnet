from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.repository import TenantScopedRepository
from app.models import (
    AuditLog,
    Business,
    BusinessUser,
    Conversation,
    KnowledgeDocument,
    Lead,
    Message,
    UsageLog,
)
from app.tenants.service import TenantService


def create_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True)
    return session_factory()


def test_tenant_service_creates_tenant_and_business():
    with create_test_session() as session:
        service = TenantService(session)

        tenant = service.create_tenant("Demo Plumbing", "demo-plumbing")
        business = service.create_business(
            tenant_id=tenant.id,
            name="Demo Plumbing",
            email="owner@example.test",
        )
        session.commit()

        assert service.get_tenant(tenant.id).slug == "demo-plumbing"
        assert service.list_businesses(tenant.id) == [business]


def test_tenant_scoped_repository_blocks_cross_tenant_reads():
    with create_test_session() as session:
        service = TenantService(session)
        tenant_a = service.create_tenant("Tenant A", "tenant-a")
        tenant_b = service.create_tenant("Tenant B", "tenant-b")
        lead_a = Lead(tenant_id=tenant_a.id, customer_name="Alice", status="new")
        lead_b = Lead(tenant_id=tenant_b.id, customer_name="Bob", status="new")
        session.add_all([lead_a, lead_b])
        session.commit()

        repo_a = TenantScopedRepository(session, Lead, tenant_a.id)

        assert repo_a.list() == [lead_a]
        assert repo_a.get(lead_a.id) == lead_a
        assert repo_a.get(lead_b.id) is None


def test_tenant_scoped_repository_rejects_wrong_tenant_add():
    with create_test_session() as session:
        service = TenantService(session)
        tenant_a = service.create_tenant("Tenant A", "tenant-a")
        tenant_b = service.create_tenant("Tenant B", "tenant-b")
        repo_a = TenantScopedRepository(session, Lead, tenant_a.id)

        try:
            repo_a.add(Lead(tenant_id=tenant_b.id, customer_name="Bob"))
        except ValueError as exc:
            assert "different tenant" in str(exc)
        else:
            raise AssertionError("Expected cross-tenant add to fail")


def test_tenant_owned_models_have_required_tenant_id_column():
    tenant_owned_models = [
        AuditLog,
        Business,
        BusinessUser,
        Conversation,
        KnowledgeDocument,
        Lead,
        Message,
        UsageLog,
    ]

    for model in tenant_owned_models:
        tenant_column = model.__table__.columns.get("tenant_id")
        assert tenant_column is not None, model.__name__
        assert tenant_column.nullable is False, model.__name__
