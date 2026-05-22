from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.models import AdminUser, AuditLog, BusinessUser, Conversation, Lead, Message, UsageLog
from app.tenants.service import TenantService
from fastapi.testclient import TestClient


def create_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
    return session_factory()


def create_client(session, monkeypatch):
    monkeypatch.setenv("ADMIN_PORTAL_SESSION_SECRET", "test-admin-secret")
    monkeypatch.setenv("BUSINESS_PORTAL_SESSION_SECRET", "test-business-secret")
    get_settings.cache_clear()
    app = create_app()

    def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db
    return TestClient(app)


def seed_admin(session, email: str = "admin@example.test"):
    admin = AdminUser(
        email=email,
        full_name="Platform Admin",
        role="super_admin",
        status="active",
    )
    session.add(admin)
    session.flush()
    return admin


def seed_business_user(session, name: str, slug: str, email: str):
    tenant_service = TenantService(session)
    tenant = tenant_service.create_tenant(name, slug)
    business = tenant_service.create_business(
        tenant_id=tenant.id,
        name=name,
        email=email,
    )
    user = BusinessUser(
        tenant_id=tenant.id,
        business_id=business.id,
        email=email,
        full_name=f"{name} Owner",
        role="owner",
        status="active",
    )
    session.add(user)
    session.flush()
    return tenant, user


def admin_login(client: TestClient, email: str = "admin@example.test") -> str:
    response = client.post("/admin/auth/login", json={"email": email})
    assert response.status_code == 200
    return response.json()["access_token"]


def business_login(client: TestClient, slug: str, email: str) -> str:
    response = client.post(
        "/business-portal/auth/login",
        json={"tenant_slug": slug, "email": email},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_admin_login_and_session_use_global_admin_role(monkeypatch):
    with create_test_session() as session:
        admin = seed_admin(session)
        session.commit()
        client = create_client(session, monkeypatch)

        token = admin_login(client)
        response = client.get("/admin/session", headers=auth_header(token))

        assert response.status_code == 200
        payload = response.json()
        assert payload["admin_id"] == admin.id
        assert payload["role"] == "super_admin"

        admin.status = "inactive"
        session.commit()
        inactive_response = client.get("/admin/session", headers=auth_header(token))

        assert inactive_response.status_code == 401


def test_admin_routes_reject_business_portal_tokens(monkeypatch):
    with create_test_session() as session:
        seed_admin(session)
        seed_business_user(
            session,
            "Demo Plumbing",
            "demo-plumbing",
            "owner@example.test",
        )
        session.commit()
        client = create_client(session, monkeypatch)
        business_token = business_login(client, "demo-plumbing", "owner@example.test")

        response = client.get("/admin/tenants", headers=auth_header(business_token))

        assert response.status_code == 401


def test_admin_can_create_manage_tenant_and_audit_actions(monkeypatch):
    with create_test_session() as session:
        seed_admin(session)
        session.commit()
        client = create_client(session, monkeypatch)
        token = admin_login(client)

        create_response = client.post(
            "/admin/tenants",
            headers=auth_header(token),
            json={
                "name": "Northside Electrical",
                "slug": "northside-electrical",
                "business_email": "hello@northside.example",
                "owner_email": "owner@northside.example",
            },
        )
        tenant_id = create_response.json()["id"]
        list_response = client.get("/admin/tenants", headers=auth_header(token))
        detail_response = client.get(
            f"/admin/tenants/{tenant_id}",
            headers=auth_header(token),
        )
        status_response = client.patch(
            f"/admin/tenants/{tenant_id}/status",
            headers=auth_header(token),
            json={"status": "suspended"},
        )

        assert create_response.status_code == 200
        assert create_response.json()["users"][0]["email"] == "owner@northside.example"
        assert list_response.status_code == 200
        assert list_response.json()[0]["slug"] == "northside-electrical"
        assert detail_response.status_code == 200
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "suspended"
        actions = set(session.scalars(select(AuditLog.action)).all())
        assert {
            "tenant_created",
            "tenant_detail_viewed",
            "tenant_status_updated",
        }.issubset(actions)
        assert {audit.tenant_id for audit in session.scalars(select(AuditLog)).all()} == {
            tenant_id
        }


def test_admin_usage_health_and_support_context_are_limited(monkeypatch):
    with create_test_session() as session:
        seed_admin(session)
        tenant, _user = seed_business_user(
            session,
            "Tenant Support Plumbing",
            "tenant-support",
            "owner@support.example",
        )
        conversation = Conversation(
            tenant_id=tenant.id,
            visitor_label="Visitor",
            status="open",
            source="website_widget",
        )
        session.add(conversation)
        session.flush()
        session.add_all(
            [
                Message(
                    tenant_id=tenant.id,
                    conversation_id=conversation.id,
                    sender_type="visitor",
                    content="My phone is 0400000000",
                ),
                Lead(
                    tenant_id=tenant.id,
                    conversation_id=conversation.id,
                    customer_name="Private Name",
                    customer_phone="0400000000",
                    job_type="blocked drain",
                    suburb="Parramatta",
                    urgency="today",
                    status="new",
                ),
                UsageLog(
                    tenant_id=tenant.id,
                    event_type="chat_message",
                    event_source="widget",
                    attributes={"safe": True},
                ),
            ]
        )
        session.commit()
        client = create_client(session, monkeypatch)
        token = admin_login(client)

        usage_response = client.get("/admin/usage", headers=auth_header(token))
        health_response = client.get("/admin/health", headers=auth_header(token))
        support_response = client.get(
            f"/admin/tenants/{tenant.id}/support-context",
            headers=auth_header(token),
        )

        assert usage_response.status_code == 200
        assert usage_response.json()["tenants_total"] == 1
        assert usage_response.json()["messages_total"] == 1
        assert health_response.status_code == 200
        assert health_response.json()["database"] == "ok"
        assert support_response.status_code == 200
        lead_payload = support_response.json()["recent_leads"][0]
        assert lead_payload["has_contact"] is True
        assert "customer_phone" not in lead_payload
        assert "customer_name" not in lead_payload
        assert support_response.json()["recent_conversations"][0]["message_count"] == 1
        assert "tenant_support_context_viewed" in set(
            session.scalars(select(AuditLog.action)).all()
        )
