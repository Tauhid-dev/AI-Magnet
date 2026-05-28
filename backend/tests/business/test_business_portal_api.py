from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import get_settings
from app.core.passwords import hash_password
from app.db.base import Base, utc_now
from app.db.session import get_db_session
from app.main import create_app
from app.models import BusinessUser, Conversation, KnowledgeDocument, Lead, Message
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
    monkeypatch.setenv("AI_PROVIDER", "test")
    monkeypatch.setenv("AI_EMBEDDING_DIMENSIONS", "16")
    monkeypatch.setenv("BUSINESS_PORTAL_SESSION_SECRET", "test-secret")
    get_settings.cache_clear()
    app = create_app()

    def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db
    return TestClient(app)


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
        password_hash=hash_password("correct-password"),
        password_updated_at=utc_now(),
    )
    session.add(user)
    session.flush()
    return tenant, user


def login(client: TestClient, slug: str, email: str) -> str:
    response = client.post(
        "/business-portal/auth/login",
        json={"tenant_slug": slug, "email": email, "password": "correct-password"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_business_portal_login_and_session_are_tenant_scoped(monkeypatch):
    with create_test_session() as session:
        tenant, _user = seed_business_user(
            session,
            "Demo Plumbing",
            "demo-plumbing",
            "owner@example.test",
        )
        session.commit()
        client = create_client(session, monkeypatch)

        token = login(client, "demo-plumbing", "owner@example.test")
        response = client.get("/business-portal/session", headers=auth_header(token))

        assert response.status_code == 200
        payload = response.json()
        assert payload["tenant_id"] == tenant.id
        assert payload["tenant_slug"] == "demo-plumbing"
        assert payload["role"] == "owner"

        tenant.status = "inactive"
        session.commit()
        inactive_response = client.get(
            "/business-portal/session",
            headers=auth_header(token),
        )

        assert inactive_response.status_code == 401


def test_business_portal_rejects_email_only_and_wrong_password(monkeypatch):
    with create_test_session() as session:
        seed_business_user(
            session,
            "Demo Plumbing",
            "demo-plumbing",
            "owner@example.test",
        )
        session.commit()
        client = create_client(session, monkeypatch)

        email_only_response = client.post(
            "/business-portal/auth/login",
            json={"tenant_slug": "demo-plumbing", "email": "owner@example.test"},
        )
        wrong_password_response = client.post(
            "/business-portal/auth/login",
            json={
                "tenant_slug": "demo-plumbing",
                "email": "owner@example.test",
                "password": "wrong-password",
            },
        )

        assert email_only_response.status_code == 422
        assert wrong_password_response.status_code == 401


def test_business_portal_logout_revokes_existing_token(monkeypatch):
    with create_test_session() as session:
        seed_business_user(
            session,
            "Demo Plumbing",
            "demo-plumbing",
            "owner@example.test",
        )
        session.commit()
        client = create_client(session, monkeypatch)
        token = login(client, "demo-plumbing", "owner@example.test")

        logout_response = client.post("/business-portal/auth/logout", headers=auth_header(token))
        revoked_response = client.get("/business-portal/session", headers=auth_header(token))

        assert logout_response.status_code == 204
        assert revoked_response.status_code == 401


def test_business_portal_locks_after_repeated_failed_passwords(monkeypatch):
    with create_test_session() as session:
        _tenant, user = seed_business_user(
            session,
            "Demo Plumbing",
            "demo-plumbing",
            "owner@example.test",
        )
        session.commit()
        monkeypatch.setenv("AUTH_FAILED_LOGIN_LIMIT", "2")
        client = create_client(session, monkeypatch)

        for _ in range(2):
            response = client.post(
                "/business-portal/auth/login",
                json={
                    "tenant_slug": "demo-plumbing",
                    "email": "owner@example.test",
                    "password": "wrong-password",
                },
            )
            assert response.status_code == 401
        locked_response = client.post(
            "/business-portal/auth/login",
            json={
                "tenant_slug": "demo-plumbing",
                "email": "owner@example.test",
                "password": "correct-password",
            },
        )

        assert locked_response.status_code == 401
        assert user.failed_login_count == 2
        assert user.locked_until is not None


def test_business_portal_blocks_cross_tenant_lead_and_conversation(monkeypatch):
    with create_test_session() as session:
        tenant_a, _user_a = seed_business_user(
            session,
            "Tenant A Plumbing",
            "tenant-a",
            "a@example.test",
        )
        tenant_b, _user_b = seed_business_user(
            session,
            "Tenant B Electrical",
            "tenant-b",
            "b@example.test",
        )
        lead_b = Lead(
            tenant_id=tenant_b.id,
            customer_name="Bob",
            customer_phone="0400000000",
            status="new",
        )
        conversation_b = Conversation(
            tenant_id=tenant_b.id,
            visitor_label="Tenant B visitor",
            status="open",
        )
        session.add_all([lead_b, conversation_b])
        session.flush()
        message_b = Message(
            tenant_id=tenant_b.id,
            conversation_id=conversation_b.id,
            sender_type="visitor",
            content="Tenant B private message",
        )
        session.add(message_b)
        session.commit()
        client = create_client(session, monkeypatch)
        token_a = login(client, "tenant-a", "a@example.test")

        lead_response = client.get(
            f"/business-portal/leads/{lead_b.id}",
            headers=auth_header(token_a),
        )
        conversation_response = client.get(
            f"/business-portal/conversations/{conversation_b.id}",
            headers=auth_header(token_a),
        )
        list_response = client.get(
            "/business-portal/conversations",
            headers=auth_header(token_a),
        )

        assert tenant_a.id != tenant_b.id
        assert lead_response.status_code == 404
        assert conversation_response.status_code == 404
        assert list_response.json() == []


def test_business_portal_updates_own_lead_status_only(monkeypatch):
    with create_test_session() as session:
        tenant_a, _user_a = seed_business_user(
            session,
            "Tenant A Plumbing",
            "tenant-a",
            "a@example.test",
        )
        tenant_b, _user_b = seed_business_user(
            session,
            "Tenant B Electrical",
            "tenant-b",
            "b@example.test",
        )
        lead_a = Lead(
            tenant_id=tenant_a.id,
            customer_name="Alice",
            customer_phone="0400000000",
            job_type="blocked drain",
            suburb="Bondi",
            urgency="today",
            status="notified",
            notification_status="sent",
        )
        lead_b = Lead(
            tenant_id=tenant_b.id,
            customer_name="Bob",
            customer_phone="0411111111",
            status="notified",
            notification_status="sent",
        )
        session.add_all([lead_a, lead_b])
        session.commit()
        client = create_client(session, monkeypatch)
        token_a = login(client, "tenant-a", "a@example.test")

        update_response = client.patch(
            f"/business-portal/leads/{lead_a.id}/status",
            headers=auth_header(token_a),
            json={"status": "contacted"},
        )
        cross_tenant_response = client.patch(
            f"/business-portal/leads/{lead_b.id}/status",
            headers=auth_header(token_a),
            json={"status": "contacted"},
        )
        invalid_response = client.patch(
            f"/business-portal/leads/{lead_a.id}/status",
            headers=auth_header(token_a),
            json={"status": "qualified"},
        )

        assert update_response.status_code == 200
        assert update_response.json()["status"] == "contacted"
        assert update_response.json()["notification_status"] == "sent"
        assert cross_tenant_response.status_code == 404
        assert invalid_response.status_code == 400


def test_business_portal_document_upload_and_widget_key_are_tenant_scoped(monkeypatch):
    with create_test_session() as session:
        tenant, _user = seed_business_user(
            session,
            "Demo Plumbing",
            "demo-plumbing",
            "owner@example.test",
        )
        session.commit()
        client = create_client(session, monkeypatch)
        token = login(client, "demo-plumbing", "owner@example.test")

        document_response = client.post(
            "/business-portal/documents",
            headers=auth_header(token),
            json={
                "filename": "services.txt",
                "content": "Blocked drains and hot water repairs in Sydney.",
                "content_type": "text/plain",
            },
        )
        widget_response = client.post(
            "/business-portal/widget/keys",
            headers=auth_header(token),
        )
        analytics_response = client.get(
            "/business-portal/analytics",
            headers=auth_header(token),
        )

        assert document_response.status_code == 200
        assert document_response.json()["status"] == "ingested"
        assert widget_response.status_code == 200
        assert widget_response.json()["widget_key"].startswith("wm_live_")
        assert widget_response.json()["embed_code"]
        assert analytics_response.json()["documents_total"] == 1
        assert analytics_response.json()["widget_status"] == "active"
        stored_document = session.scalars(select(KnowledgeDocument)).one()
        assert stored_document.tenant_id == tenant.id
