import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.models import AdminUser, BusinessUser, UsageLog
from app.tenants.service import TenantService


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


def create_client(session, monkeypatch) -> TestClient:
    monkeypatch.setenv("ADMIN_PORTAL_SESSION_SECRET", "test-admin-secret")
    monkeypatch.setenv("BUSINESS_PORTAL_SESSION_SECRET", "test-business-secret")
    get_settings.cache_clear()
    app = create_app()

    def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db
    return TestClient(app)


def seed_admin(session, email: str = "admin@example.test") -> AdminUser:
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


def login_admin(client: TestClient, email: str = "admin@example.test") -> str:
    response = client.post("/admin/auth/login", json={"email": email})
    assert response.status_code == 200
    return response.json()["access_token"]


def login_business(client: TestClient, tenant_slug: str, email: str) -> str:
    response = client.post(
        "/business-portal/auth/login",
        json={"tenant_slug": tenant_slug, "email": email},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_production_runtime_rejects_placeholder_secrets_and_wildcard_cors(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ENABLE_API_DOCS", "true")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*")
    monkeypatch.setenv("BUSINESS_PORTAL_SESSION_SECRET", "change-me-before-production")
    monkeypatch.setenv("ADMIN_PORTAL_SESSION_SECRET", "change-me-before-production")
    get_settings.cache_clear()

    with pytest.raises(RuntimeError, match="Production security configuration invalid"):
        create_app()

    get_settings.cache_clear()


def test_security_headers_are_added_to_api_responses(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in response.headers["Permissions-Policy"]


def test_cross_portal_tokens_are_not_accepted_for_sensitive_routes(monkeypatch):
    with create_test_session() as session:
        seed_admin(session)
        seed_business_user(
            session,
            "Tenant A Plumbing",
            "tenant-a",
            "owner@tenant-a.example",
        )
        session.commit()
        client = create_client(session, monkeypatch)

        admin_token = login_admin(client)
        business_token = login_business(client, "tenant-a", "owner@tenant-a.example")

        admin_with_business_token = client.get(
            "/admin/usage",
            headers=auth_header(business_token),
        )
        portal_with_admin_token = client.get(
            "/business-portal/leads",
            headers=auth_header(admin_token),
        )

        assert admin_with_business_token.status_code == 401
        assert portal_with_admin_token.status_code == 401


def test_business_analytics_never_counts_another_tenant_usage(monkeypatch):
    with create_test_session() as session:
        tenant_a, _user_a = seed_business_user(
            session,
            "Tenant A Plumbing",
            "tenant-a",
            "owner@tenant-a.example",
        )
        tenant_b, _user_b = seed_business_user(
            session,
            "Tenant B Electrical",
            "tenant-b",
            "owner@tenant-b.example",
        )
        session.add_all(
            [
                UsageLog(
                    tenant_id=tenant_a.id,
                    event_type="tenant_a_safe_event",
                    event_source="security_test",
                    attributes={"safe": True},
                ),
                UsageLog(
                    tenant_id=tenant_b.id,
                    event_type="tenant_b_private_event",
                    event_source="security_test",
                    attributes={"safe": False},
                ),
            ]
        )
        session.commit()
        client = create_client(session, monkeypatch)
        token_a = login_business(client, "tenant-a", "owner@tenant-a.example")

        response = client.get("/business-portal/analytics", headers=auth_header(token_a))

        assert response.status_code == 200
        payload = response.json()
        assert payload["usage_events_total"] == 1
        assert payload["recent_usage"][0]["event_type"] == "tenant_a_safe_event"
        assert {item["label"] for item in payload["usage_event_counts"]} == {
            "tenant_a_safe_event"
        }
