from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.billing import BillingService
from app.core.config import Settings
from app.db.base import Base, utc_now
from app.models import Conversation, KnowledgeDocument, UsageLog
from app.tenants.service import TenantService
from app.usage import UsageEventSource, UsageEventType
from app.usage.quotas import QuotaService


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


def seed_tenant(session):
    tenant = TenantService(session).create_tenant("Quota Test Plumbing", "quota-test")
    TenantService(session).create_business(
        tenant_id=tenant.id,
        name="Quota Test Plumbing",
        email="owner@quota-test.example",
    )
    return tenant


def test_quota_snapshot_counts_monthly_tokens_cost_storage_and_blocks():
    with create_test_session() as session:
        tenant = seed_tenant(session)
        session.add_all(
            [
                Conversation(tenant_id=tenant.id, status="open", source="website_widget"),
                KnowledgeDocument(
                    tenant_id=tenant.id,
                    filename="pricing.pdf",
                    status="ingested",
                    file_size_bytes=2 * 1024 * 1024,
                ),
                UsageLog(
                    tenant_id=tenant.id,
                    event_type=UsageEventType.ASSISTANT_RESPONSE_GENERATED,
                    event_source=UsageEventSource.CHAT_WIDGET,
                    attributes={
                        "estimated_prompt_tokens": 80,
                        "estimated_response_tokens": 30,
                        "estimated_total_tokens": 110,
                        "estimated_cost_cents": 1.25,
                    },
                ),
                UsageLog(
                    tenant_id=tenant.id,
                    event_type=UsageEventType.WEBSITE_CRAWL_COMPLETED,
                    event_source=UsageEventSource.RAG_INGESTION,
                    attributes={"pages_ingested": 3},
                ),
            ]
        )
        session.commit()
        settings = Settings(
            tenant_quota_chat_conversations_per_month=1,
            tenant_quota_ai_responses_per_month=1,
            tenant_quota_tokens_per_month=100,
            tenant_budget_monthly_cents=1,
            tenant_quota_documents_total=1,
            tenant_quota_storage_mb=1,
            tenant_quota_pages_crawled_per_month=2,
            quota_warning_threshold_percent=80,
        )

        snapshot = QuotaService(session, settings).snapshot(tenant.id)
        by_key = {metric.key: metric for metric in snapshot.metrics}

        assert by_key["chat_conversations"].blocked is True
        assert by_key["ai_responses"].blocked is True
        assert by_key["estimated_tokens"].used == 110
        assert by_key["estimated_cost_cents"].used == 1.25
        assert by_key["storage_mb"].used == 2
        assert by_key["pages_crawled"].blocked is True
        assert "Estimated AI tokens" in snapshot.blocked_reasons


def test_quota_block_event_is_recorded_without_customer_content():
    with create_test_session() as session:
        tenant = seed_tenant(session)
        service = QuotaService(session)

        service.record_quota_block(
            tenant_id=tenant.id,
            operation="chat_message",
            blocked_reasons=["Estimated AI cost"],
        )
        event = session.query(UsageLog).one()

        assert event.tenant_id == tenant.id
        assert event.event_type == UsageEventType.QUOTA_LIMIT_EXCEEDED
        assert event.attributes == {
            "operation": "chat_message",
            "blocked_reasons": ["Estimated AI cost"],
        }


def test_quota_service_uses_manual_paid_beta_entitlements_and_blocks_paused_status():
    with create_test_session() as session:
        tenant = seed_tenant(session)
        BillingService(session).set_manual_subscription(
            tenant_id=tenant.id,
            plan_code="starter_manual",
            status="active",
            admin_id="admin-test",
        )
        session.commit()

        service = QuotaService(session)
        snapshot = service.snapshot(tenant.id)
        by_key = {metric.key: metric for metric in snapshot.metrics}

        assert by_key["chat_conversations"].limit == 1000
        assert by_key["estimated_cost_cents"].limit == 4000
        assert service.chat_start_blockers(tenant.id) == []

        subscription = BillingService(session).get_subscription(tenant.id)
        assert subscription is not None
        subscription.status = "paused"
        session.commit()

        assert "Subscription paused" in service.chat_start_blockers(tenant.id)
        assert "Subscription paused" in service.document_blockers(tenant.id)


def test_quota_service_blocks_expired_manual_trial():
    with create_test_session() as session:
        tenant = seed_tenant(session)
        subscription = BillingService(session).set_manual_subscription(
            tenant_id=tenant.id,
            plan_code="pilot_trial",
            status="trialing",
            admin_id="admin-test",
        )
        subscription.trial_ends_at = utc_now() - timedelta(days=1)
        session.commit()

        blockers = QuotaService(session).ai_response_blockers(tenant.id)

        assert blockers == ["Subscription trial expired"]
