from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.analytics.service import AnalyticsService
from app.db.base import Base
from app.models import (
    Conversation,
    GlobalAuditLog,
    KnowledgeDocument,
    Lead,
    Message,
    NotificationDelivery,
    UsageLog,
)
from app.tenants.service import TenantService
from app.usage import UsageEventSource, UsageEventType, UsageService


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


def seed_tenant(session, name: str, slug: str):
    tenant = TenantService(session).create_tenant(name, slug)
    TenantService(session).create_business(
        tenant_id=tenant.id,
        name=name,
        email=f"owner@{slug}.example",
    )
    return tenant


def test_usage_service_records_tenant_scoped_safe_events():
    with create_test_session() as session:
        tenant = seed_tenant(session, "Tenant A Plumbing", "tenant-a")

        event = UsageService(session).record_event(
            tenant_id=tenant.id,
            event_type=UsageEventType.WIDGET_KEY_CREATED,
            event_source=UsageEventSource.BUSINESS_PORTAL,
            attributes={"widget_config_id": "widget-1"},
        )

        assert event.tenant_id == tenant.id
        assert event.event_type == "widget_key_created"
        assert event.attributes == {"widget_config_id": "widget-1"}


def test_tenant_analytics_snapshot_never_counts_another_tenant():
    with create_test_session() as session:
        tenant_a = seed_tenant(session, "Tenant A Plumbing", "tenant-a")
        tenant_b = seed_tenant(session, "Tenant B Electrical", "tenant-b")
        conversation_a = Conversation(
            tenant_id=tenant_a.id,
            visitor_label="Visitor A",
            status="open",
            source="website_widget",
        )
        conversation_b = Conversation(
            tenant_id=tenant_b.id,
            visitor_label="Visitor B",
            status="open",
            source="website_widget",
        )
        session.add_all([conversation_a, conversation_b])
        session.flush()
        session.add_all(
            [
                KnowledgeDocument(
                    tenant_id=tenant_a.id,
                    filename="a.txt",
                    status="ingested",
                ),
                KnowledgeDocument(
                    tenant_id=tenant_b.id,
                    filename="b.txt",
                    status="failed",
                ),
                Message(
                    tenant_id=tenant_a.id,
                    conversation_id=conversation_a.id,
                    sender_type="visitor",
                    content="Tenant A visitor message",
                ),
                Message(
                    tenant_id=tenant_a.id,
                    conversation_id=conversation_a.id,
                    sender_type="assistant",
                    content="Tenant A assistant message",
                ),
                Message(
                    tenant_id=tenant_b.id,
                    conversation_id=conversation_b.id,
                    sender_type="assistant",
                    content="Tenant B assistant message",
                ),
                Lead(
                    tenant_id=tenant_a.id,
                    conversation_id=conversation_a.id,
                    customer_name="Alex",
                    status="qualified",
                    notification_status="sent",
                ),
                Lead(
                    tenant_id=tenant_b.id,
                    conversation_id=conversation_b.id,
                    customer_name="Private Tenant B",
                    status="notified",
                    notification_status="sent",
                ),
                NotificationDelivery(
                    tenant_id=tenant_a.id,
                    lead_id=None,
                    notification_type="lead_qualified",
                    recipient_email="owner@tenant-a.example",
                    subject="Lead",
                    body_text="Safe summary",
                    status="sent",
                ),
                UsageLog(
                    tenant_id=tenant_a.id,
                    event_type=UsageEventType.ASSISTANT_RESPONSE_GENERATED,
                    event_source=UsageEventSource.CHAT_WIDGET,
                    attributes={"conversation_id": conversation_a.id},
                ),
                UsageLog(
                    tenant_id=tenant_b.id,
                    event_type=UsageEventType.ASSISTANT_RESPONSE_GENERATED,
                    event_source=UsageEventSource.CHAT_WIDGET,
                    attributes={"conversation_id": conversation_b.id},
                ),
            ]
        )
        session.commit()

        snapshot = AnalyticsService(session).tenant_snapshot(tenant_a.id)

        assert snapshot.documents_total == 1
        assert snapshot.documents_ingested == 1
        assert snapshot.leads_total == 1
        assert snapshot.leads_qualified == 1
        assert snapshot.conversations_total == 1
        assert snapshot.messages_total == 2
        assert snapshot.assistant_messages_total == 1
        assert snapshot.ai_responses_total == 1
        assert snapshot.lead_notifications_sent == 1
        assert [(item.label, item.count) for item in snapshot.document_status_counts] == [
            ("ingested", 1)
        ]
        assert "notified" not in {item.label for item in snapshot.lead_status_counts}


def test_platform_analytics_snapshot_aggregates_without_pii():
    with create_test_session() as session:
        tenant_a = seed_tenant(session, "Tenant A Plumbing", "tenant-a")
        tenant_b = seed_tenant(session, "Tenant B Electrical", "tenant-b")
        session.add_all(
            [
                KnowledgeDocument(tenant_id=tenant_a.id, filename="a.txt", status="ingested"),
                KnowledgeDocument(tenant_id=tenant_b.id, filename="b.txt", status="failed"),
                Lead(tenant_id=tenant_a.id, customer_name="Private A", status="qualified"),
                Lead(tenant_id=tenant_b.id, customer_name="Private B", status="notified"),
                UsageLog(
                    tenant_id=tenant_a.id,
                    event_type=UsageEventType.ASSISTANT_RESPONSE_GENERATED,
                    event_source=UsageEventSource.CHAT_WIDGET,
                    attributes={"safe": True},
                ),
                UsageLog(
                    tenant_id=tenant_a.id,
                    event_type=UsageEventType.RATE_LIMIT_EXCEEDED,
                    event_source=UsageEventSource.CHAT_WIDGET,
                    attributes={"scope": "chat_start_public"},
                ),
                GlobalAuditLog(
                    action=UsageEventType.RATE_LIMIT_EXCEEDED,
                    target_type="rate_limit",
                    attributes={"scope": "admin_login"},
                ),
            ]
        )
        session.commit()

        snapshot = AnalyticsService(session).platform_snapshot()

        assert snapshot.tenants_total == 2
        assert snapshot.documents_total == 2
        assert snapshot.documents_ingested == 1
        assert snapshot.leads_total == 2
        assert snapshot.leads_qualified == 1
        assert snapshot.ai_responses_total == 1
        assert snapshot.rate_limit_events_total == 2
        assert {tenant.tenant_slug for tenant in snapshot.tenant_usage} == {
            "tenant-a",
            "tenant-b",
        }
        assert all(not hasattr(tenant, "customer_name") for tenant in snapshot.tenant_usage)
