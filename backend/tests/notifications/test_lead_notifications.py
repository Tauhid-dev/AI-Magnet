from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db.base import Base
from app.leads.workflow import LeadWorkflowService
from app.models import Lead, NotificationDelivery
from app.notifications.service import NotificationService
from app.providers.email.base import EmailMessagePayload, EmailSendResult
from app.tenants.service import TenantService


class RecordingEmailProvider:
    def __init__(self, success: bool = True) -> None:
        self.success = success
        self.messages: list[EmailMessagePayload] = []

    def send(self, message: EmailMessagePayload) -> EmailSendResult:
        self.messages.append(message)
        if not self.success:
            return EmailSendResult(success=False, error_message="SMTP unavailable")
        return EmailSendResult(success=True, provider_message_id="test-message-id")


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


def create_qualified_lead(session, tenant_id: str) -> Lead:
    lead = Lead(
        tenant_id=tenant_id,
        customer_name="Alex",
        customer_phone="0412 345 678",
        customer_email="alex@example.test",
        job_type="blocked drain",
        suburb="Bondi",
        urgency="today",
        status="new",
        notes="Please call after 4pm.",
    )
    session.add(lead)
    LeadWorkflowService(session).evaluate_qualification(lead)
    return lead


def test_qualified_lead_notification_is_tenant_scoped_and_marks_sent():
    with create_test_session() as session:
        tenant_service = TenantService(session)
        tenant_a = tenant_service.create_tenant("Tenant A Plumbing", "tenant-a")
        tenant_service.create_business(tenant_a.id, "Tenant A Plumbing", "owner-a@example.test")
        tenant_b = tenant_service.create_tenant("Tenant B Electrical", "tenant-b")
        tenant_service.create_business(tenant_b.id, "Tenant B Electrical", "owner-b@example.test")
        session.add(
            Lead(
                tenant_id=tenant_b.id,
                customer_name="Private Tenant B",
                job_type="switchboard upgrade",
                status="qualified",
            )
        )
        lead = create_qualified_lead(session, tenant_a.id)
        provider = RecordingEmailProvider()

        result = NotificationService(
            session,
            email_provider=provider,
        ).queue_and_send_lead_notification(
            tenant_a.id,
            lead,
        )

        assert result.delivery is not None
        assert result.delivery.tenant_id == tenant_a.id
        assert result.delivery.status == "sent"
        assert lead.status == "notified"
        assert lead.notification_status == "sent"
        assert lead.last_notified_at is not None
        assert provider.messages[0].to_email == "owner-a@example.test"
        assert "blocked drain" in provider.messages[0].body_text
        assert "Private Tenant B" not in provider.messages[0].body_text
        deliveries = list(session.scalars(select(NotificationDelivery)))
        assert {delivery.tenant_id for delivery in deliveries} == {tenant_a.id}


def test_failed_notification_is_left_for_retry_without_duplicate_send():
    with create_test_session() as session:
        tenant_service = TenantService(session)
        tenant = tenant_service.create_tenant("Demo Plumbing", "demo-plumbing")
        tenant_service.create_business(tenant.id, "Demo Plumbing", "owner@example.test")
        lead = create_qualified_lead(session, tenant.id)
        provider = RecordingEmailProvider(success=False)
        service = NotificationService(session, email_provider=provider)

        result = service.queue_and_send_lead_notification(tenant.id, lead)
        duplicate = service.queue_lead_notification(tenant.id, lead)

        assert result.delivery is not None
        assert result.delivery.status == "retry_scheduled"
        assert result.delivery.attempts == 1
        assert lead.notification_status == "retry_scheduled"
        assert duplicate.delivery is None
        assert duplicate.reason == "notification_already_exists"
        assert len(provider.messages) == 1
