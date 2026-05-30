import time

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.admin.auth import AdminPortalAuthService
from app.core.config import Settings, get_settings
from app.core.passwords import hash_password
from app.core.rate_limit import rate_limiter
from app.core.totp import generate_totp_code
from app.db.base import Base, utc_now
from app.db.session import get_db_session
from app.main import create_app
from app.models import (
    AdminUser,
    AuditLog,
    BackgroundJob,
    BusinessUser,
    Conversation,
    GlobalAuditLog,
    Lead,
    Message,
    Tenant,
    UsageLog,
    WorkerHeartbeat,
)
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
    rate_limiter.reset()
    get_settings.cache_clear()
    app = create_app()

    def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db
    return TestClient(app)


def seed_admin(
    session,
    email: str = "admin@example.test",
    *,
    mfa_required: bool = False,
    mfa_secret: str | None = None,
):
    admin = AdminUser(
        email=email,
        full_name="Platform Admin",
        role="super_admin",
        status="active",
        password_hash=hash_password("correct-admin-password"),
        password_updated_at=utc_now(),
        mfa_required=mfa_required,
        mfa_secret=mfa_secret,
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
        password_hash=hash_password("correct-password"),
        password_updated_at=utc_now(),
    )
    session.add(user)
    session.flush()
    return tenant, user


def admin_login(client: TestClient, email: str = "admin@example.test") -> str:
    response = client.post(
        "/admin/auth/login",
        json={"email": email, "password": "correct-admin-password"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def business_login(client: TestClient, slug: str, email: str) -> str:
    response = client.post(
        "/business-portal/auth/login",
        json={"tenant_slug": slug, "email": email, "password": "correct-password"},
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


def test_admin_login_rejects_email_only_and_supports_totp_mfa(monkeypatch):
    with create_test_session() as session:
        mfa_secret = "JBSWY3DPEHPK3PXP"
        admin = seed_admin(session)
        admin.mfa_required = True
        admin.mfa_secret = mfa_secret
        session.commit()
        client = create_client(session, monkeypatch)

        email_only_response = client.post("/admin/auth/login", json={"email": admin.email})
        missing_mfa_response = client.post(
            "/admin/auth/login",
            json={"email": admin.email, "password": "correct-admin-password"},
        )
        code = generate_totp_code(mfa_secret, int(time.time() // 30))
        mfa_response = client.post(
            "/admin/auth/login",
            json={
                "email": admin.email,
                "password": "correct-admin-password",
                "mfa_code": code,
            },
        )

        assert email_only_response.status_code == 422
        assert missing_mfa_response.status_code == 401
        assert mfa_response.status_code == 200


def test_production_super_admin_without_mfa_cannot_login():
    with create_test_session() as session:
        admin = seed_admin(session, mfa_required=False, mfa_secret=None)
        session.commit()
        settings = Settings(
            environment="production",
            admin_portal_session_secret="a" * 48,
        )

        result = AdminPortalAuthService(session, settings).login(
            email=admin.email,
            password="correct-admin-password",
        )

        assert result is None


def test_production_super_admin_requires_configured_valid_mfa():
    with create_test_session() as session:
        admin = seed_admin(
            session,
            mfa_required=True,
            mfa_secret="JBSWY3DPEHPK3PXP",
        )
        session.commit()
        settings = Settings(
            environment="production",
            admin_portal_session_secret="a" * 48,
        )
        service = AdminPortalAuthService(session, settings)
        valid_code = generate_totp_code(admin.mfa_secret, int(time.time() // 30))

        missing_mfa = service.login(
            email=admin.email,
            password="correct-admin-password",
        )
        invalid_mfa = service.login(
            email=admin.email,
            password="correct-admin-password",
            mfa_code="000000",
        )
        valid_mfa = service.login(
            email=admin.email,
            password="correct-admin-password",
            mfa_code=valid_code,
        )

        assert missing_mfa is None
        assert invalid_mfa is None
        assert valid_mfa is not None


def test_production_super_admin_missing_mfa_secret_cannot_login():
    with create_test_session() as session:
        admin = seed_admin(session, mfa_required=True, mfa_secret=None)
        session.commit()
        settings = Settings(
            environment="production",
            admin_portal_session_secret="a" * 48,
        )

        result = AdminPortalAuthService(session, settings).login(
            email=admin.email,
            password="correct-admin-password",
            mfa_code="123456",
        )

        assert result is None


def test_local_admin_without_mfa_remains_allowed_for_local_dev():
    with create_test_session() as session:
        admin = seed_admin(session, mfa_required=False, mfa_secret=None)
        session.commit()
        settings = Settings(
            environment="local",
            admin_portal_session_secret="a" * 48,
        )

        result = AdminPortalAuthService(session, settings).login(
            email=admin.email,
            password="correct-admin-password",
        )

        assert result is not None


def test_admin_logout_revokes_existing_token(monkeypatch):
    with create_test_session() as session:
        seed_admin(session)
        session.commit()
        client = create_client(session, monkeypatch)
        token = admin_login(client)

        logout_response = client.post("/admin/auth/logout", headers=auth_header(token))
        revoked_response = client.get("/admin/session", headers=auth_header(token))

        assert logout_response.status_code == 204
        assert revoked_response.status_code == 401


def test_admin_locks_after_repeated_failed_passwords(monkeypatch):
    with create_test_session() as session:
        admin = seed_admin(session)
        session.commit()
        monkeypatch.setenv("AUTH_FAILED_LOGIN_LIMIT", "2")
        client = create_client(session, monkeypatch)

        for _ in range(2):
            response = client.post(
                "/admin/auth/login",
                json={"email": admin.email, "password": "wrong-password"},
            )
            assert response.status_code == 401
        locked_response = client.post(
            "/admin/auth/login",
            json={"email": admin.email, "password": "correct-admin-password"},
        )

        assert locked_response.status_code == 401
        assert admin.failed_login_count == 2
        assert admin.locked_until is not None


def test_admin_login_rate_limit_records_global_safe_event(monkeypatch):
    with create_test_session() as session:
        admin = seed_admin(session)
        session.commit()
        monkeypatch.setenv("RATE_LIMIT_LOGIN_PER_MINUTE", "1")
        client = create_client(session, monkeypatch)

        first_response = client.post(
            "/admin/auth/login",
            json={
                "email": admin.email,
                "password": "wrong-admin-password",
                "mfa_code": "123456",
            },
        )
        assert first_response.status_code == 401
        assert (
            session.scalars(
                select(GlobalAuditLog).where(GlobalAuditLog.action == "rate_limit_exceeded")
            ).all()
            == []
        )

        limited_response = client.post(
            "/admin/auth/login",
            json={
                "email": admin.email,
                "password": "wrong-admin-password",
                "mfa_code": "654321",
            },
        )

        assert limited_response.status_code == 429
        assert int(limited_response.headers["Retry-After"]) > 0
        event = session.scalars(
            select(GlobalAuditLog).where(GlobalAuditLog.action == "rate_limit_exceeded")
        ).one()
        assert event.tenant_id is None
        assert event.target_type == "rate_limit"
        assert event.attributes["scope"] == "admin_login"
        assert event.attributes["actor_category"] == "admin_login"
        assert event.attributes["route"] == "/admin/auth/login"
        serialized = str(event.attributes).lower()
        assert admin.email not in serialized
        assert "wrong-admin-password" not in serialized
        assert "123456" not in serialized
        assert "654321" not in serialized


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
                "owner_password": "tenant-owner-password",
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
        missing_owner_password_response = client.post(
            "/admin/tenants",
            headers=auth_header(token),
            json={
                "name": "Missing Password Co",
                "slug": "missing-password-co",
                "owner_email": "owner@missing-password.example",
            },
        )

        assert create_response.status_code == 200
        assert create_response.json()["users"][0]["email"] == "owner@northside.example"
        assert session.scalars(select(BusinessUser.password_hash)).first() is not None
        assert list_response.status_code == 200
        assert list_response.json()[0]["slug"] == "northside-electrical"
        assert detail_response.status_code == 200
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "suspended"
        assert missing_owner_password_response.status_code == 400
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
                BackgroundJob(
                    tenant_id=tenant.id,
                    job_type="test.job",
                    payload={},
                    status="queued",
                    scheduled_at=utc_now(),
                ),
                WorkerHeartbeat(
                    worker_id="test-worker",
                    queue_name="default",
                    status="idle",
                    last_seen_at=utc_now(),
                ),
            ]
        )
        session.commit()
        client = create_client(session, monkeypatch)
        token = admin_login(client)

        usage_response = client.get("/admin/usage", headers=auth_header(token))
        health_response = client.get("/admin/health", headers=auth_header(token))
        jobs_response = client.get("/admin/jobs", headers=auth_header(token))
        workers_response = client.get(
            "/admin/worker-heartbeats",
            headers=auth_header(token),
        )
        support_response = client.get(
            f"/admin/tenants/{tenant.id}/support-context",
            headers=auth_header(token),
        )

        assert usage_response.status_code == 200
        assert usage_response.json()["tenants_total"] == 1
        assert usage_response.json()["messages_total"] == 1
        assert health_response.status_code == 200
        assert health_response.json()["database"] == "ok"
        assert health_response.json()["queued_jobs"] == 1
        assert health_response.json()["active_workers"] == 1
        assert jobs_response.status_code == 200
        assert jobs_response.json()[0]["job_type"] == "test.job"
        assert "payload" not in jobs_response.json()[0]
        assert workers_response.status_code == 200
        assert workers_response.json()[0]["worker_id"] == "test-worker"
        assert support_response.status_code == 200
        lead_payload = support_response.json()["recent_leads"][0]
        assert lead_payload["has_contact"] is True
        assert "customer_phone" not in lead_payload
        assert "customer_name" not in lead_payload
        assert support_response.json()["recent_conversations"][0]["message_count"] == 1
        assert "tenant_support_context_viewed" in set(
            session.scalars(select(AuditLog.action)).all()
        )


def test_admin_privacy_lifecycle_export_offboard_delete_and_global_audit(monkeypatch):
    with create_test_session() as session:
        seed_admin(session)
        tenant, _user = seed_business_user(
            session,
            "Privacy Plumbing",
            "privacy-plumbing",
            "owner@privacy.example",
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
                    content="My email is customer@example.test",
                ),
                Lead(
                    tenant_id=tenant.id,
                    conversation_id=conversation.id,
                    customer_name="Private Customer",
                    customer_email="customer@example.test",
                    customer_phone="0400000000",
                    status="qualified",
                ),
                UsageLog(
                    tenant_id=tenant.id,
                    event_type="privacy_test_event",
                    event_source="test",
                    attributes={"safe": True},
                ),
            ]
        )
        session.commit()
        client = create_client(session, monkeypatch)
        token = admin_login(client)

        export_response = client.get(
            f"/admin/tenants/{tenant.id}/privacy-export",
            headers=auth_header(token),
        )
        audit_response = client.get("/admin/audit-logs", headers=auth_header(token))
        offboard_response = client.post(
            f"/admin/tenants/{tenant.id}/offboard",
            headers=auth_header(token),
            json={"retention_days": 14},
        )
        wrong_delete_response = client.post(
            f"/admin/tenants/{tenant.id}/delete-data",
            headers=auth_header(token),
            json={"confirm_slug": "wrong-slug", "confirm_delete": True},
        )
        delete_response = client.post(
            f"/admin/tenants/{tenant.id}/delete-data",
            headers=auth_header(token),
            json={"confirm_slug": "privacy-plumbing", "confirm_delete": True},
        )

        assert export_response.status_code == 200
        export_payload = export_response.json()["data"]
        assert export_payload["tenant"]["slug"] == "privacy-plumbing"
        assert export_payload["business_users"][0]["email"] == "owner@privacy.example"
        assert "password_hash" not in export_payload["business_users"][0]
        assert export_payload["leads"][0]["customer_name"] == "Private Customer"
        assert audit_response.status_code == 200
        assert any(
            event["scope"] == "global"
            and event["action"] == "tenant_privacy_export_generated"
            for event in audit_response.json()
        )
        assert offboard_response.status_code == 200
        assert offboard_response.json()["status"] == "offboarding"
        assert offboard_response.json()["data_retention_until"] is not None
        assert wrong_delete_response.status_code == 400
        assert delete_response.status_code == 200
        assert delete_response.json()["status"] == "deleted"
        assert (
            session.scalar(select(func.count()).select_from(Tenant).where(Tenant.id == tenant.id))
            == 0
        )

        global_actions = set(session.scalars(select(GlobalAuditLog.action)).all())
        assert {
            "admin_login_succeeded",
            "tenant_privacy_export_generated",
            "tenant_offboarded",
            "tenant_data_deleted",
        }.issubset(global_actions)
        login_event = session.scalars(
            select(GlobalAuditLog).where(GlobalAuditLog.action == "admin_login_succeeded")
        ).first()
        assert login_event.attributes["email"]["redacted"] is True


def test_admin_can_manage_manual_paid_beta_subscription_and_audit_actions(monkeypatch):
    with create_test_session() as session:
        seed_admin(session)
        tenant, _user = seed_business_user(
            session,
            "Billing Plumbing",
            "billing-plumbing",
            "owner@billing.example",
        )
        session.commit()
        client = create_client(session, monkeypatch)
        token = admin_login(client)

        plans_response = client.get("/admin/billing/plans", headers=auth_header(token))
        missing_subscription_response = client.get(
            f"/admin/tenants/{tenant.id}/subscription",
            headers=auth_header(token),
        )
        create_response = client.put(
            f"/admin/tenants/{tenant.id}/subscription",
            headers=auth_header(token),
            json={
                "plan_code": "pilot_trial",
                "status": "trialing",
                "billing_contact_email": "billing@billing.example",
                "manual_reference": "approval-001",
                "notes": "Approved for controlled paid-beta trial.",
            },
        )
        update_response = client.put(
            f"/admin/tenants/{tenant.id}/subscription",
            headers=auth_header(token),
            json={
                "plan_code": "starter_manual",
                "status": "active",
                "billing_contact_email": "billing@billing.example",
                "manual_reference": "invoice-001",
            },
        )
        invalid_response = client.put(
            f"/admin/tenants/{tenant.id}/subscription",
            headers=auth_header(token),
            json={"plan_code": "unknown", "status": "active"},
        )

        assert plans_response.status_code == 200
        assert {plan["code"] for plan in plans_response.json()} >= {
            "pilot_trial",
            "starter_manual",
        }
        assert missing_subscription_response.status_code == 200
        assert missing_subscription_response.json() is None
        assert create_response.status_code == 200
        assert create_response.json()["status"] == "trialing"
        assert create_response.json()["billing_mode"] == "manual"
        assert create_response.json()["trial_ends_at"] is not None
        assert update_response.status_code == 200
        assert update_response.json()["plan_code"] == "starter_manual"
        assert update_response.json()["monthly_price_cents"] == 9900
        assert invalid_response.status_code == 400

        actions = set(session.scalars(select(AuditLog.action)).all())
        global_actions = set(session.scalars(select(GlobalAuditLog.action)).all())
        assert {
            "tenant_subscription_created",
            "tenant_subscription_updated",
        }.issubset(actions)
        assert {
            "tenant_subscription_created",
            "tenant_subscription_updated",
        }.issubset(global_actions)
