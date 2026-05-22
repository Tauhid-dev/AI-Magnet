"""Tenant-scoped lead notification workflow."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.base import utc_now
from app.leads.workflow import LEAD_STATUS_QUALIFIED, LeadWorkflowService
from app.models.lead import Lead
from app.models.notification import BusinessNotificationSetting, NotificationDelivery
from app.models.tenant import Business
from app.providers.email import EmailMessagePayload, EmailProvider, get_email_provider
from app.notifications.templates import lead_notification_body, lead_notification_subject


NOTIFICATION_TYPE_LEAD_QUALIFIED = "lead_qualified"
NOTIFICATION_STATUS_NOT_QUEUED = "not_queued"
NOTIFICATION_STATUS_QUEUED = "queued"
NOTIFICATION_STATUS_RETRY_SCHEDULED = "retry_scheduled"
NOTIFICATION_STATUS_SENT = "sent"
NOTIFICATION_STATUS_FAILED = "failed"
NOTIFIABLE_LEAD_STATUSES = {LEAD_STATUS_QUALIFIED}


@dataclass(frozen=True)
class NotificationQueueResult:
    """Result after attempting to queue or send a notification."""

    delivery: NotificationDelivery | None
    reason: str | None = None


class NotificationService:
    """Queue and process tenant-owned notifications."""

    def __init__(
        self,
        session: Session,
        settings: Settings | None = None,
        email_provider: EmailProvider | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.email_provider = email_provider or get_email_provider(self.settings)

    def queue_lead_notification(self, tenant_id: str, lead: Lead) -> NotificationQueueResult:
        """Queue a notification for a qualified lead if recipient settings allow it."""
        if lead.tenant_id != tenant_id:
            return NotificationQueueResult(None, reason="lead_tenant_mismatch")
        if lead.status not in NOTIFIABLE_LEAD_STATUSES:
            return NotificationQueueResult(None, reason="lead_not_qualified")
        if lead.notification_status in {
            NOTIFICATION_STATUS_QUEUED,
            NOTIFICATION_STATUS_RETRY_SCHEDULED,
            NOTIFICATION_STATUS_SENT,
        }:
            return NotificationQueueResult(None, reason="notification_already_exists")

        recipient = self.resolve_recipient_email(tenant_id)
        if recipient is None:
            lead.notification_status = NOTIFICATION_STATUS_FAILED
            self.session.flush()
            return NotificationQueueResult(None, reason="no_recipient_email")

        delivery = NotificationDelivery(
            tenant_id=tenant_id,
            lead_id=lead.id,
            notification_type=NOTIFICATION_TYPE_LEAD_QUALIFIED,
            recipient_email=recipient,
            subject=lead_notification_subject(lead),
            body_text=lead_notification_body(lead),
            status=NOTIFICATION_STATUS_QUEUED,
            attempts=0,
            max_attempts=3,
            next_attempt_at=utc_now(),
        )
        lead.notification_status = NOTIFICATION_STATUS_QUEUED
        self.session.add(delivery)
        self.session.flush()
        return NotificationQueueResult(delivery)

    def queue_and_send_lead_notification(
        self,
        tenant_id: str,
        lead: Lead,
    ) -> NotificationQueueResult:
        """Queue and immediately process a qualified lead notification."""
        result = self.queue_lead_notification(tenant_id, lead)
        if result.delivery is None:
            return result
        self.send_delivery(result.delivery)
        return result

    def process_due_notifications(self, limit: int = 25) -> list[NotificationDelivery]:
        """Process queued notifications due for delivery."""
        now = utc_now()
        statement = (
            select(NotificationDelivery)
            .where(
                NotificationDelivery.status.in_(
                    [NOTIFICATION_STATUS_QUEUED, NOTIFICATION_STATUS_RETRY_SCHEDULED]
                ),
                NotificationDelivery.next_attempt_at <= now,
            )
            .order_by(NotificationDelivery.created_at)
            .limit(limit)
        )
        deliveries = list(self.session.scalars(statement))
        for delivery in deliveries:
            self.send_delivery(delivery)
        return deliveries

    def send_delivery(self, delivery: NotificationDelivery) -> NotificationDelivery:
        """Send one queued delivery and update delivery/lead state."""
        delivery.attempts += 1
        payload = EmailMessagePayload(
            to_email=delivery.recipient_email,
            subject=delivery.subject,
            body_text=delivery.body_text,
            from_email=self.settings.smtp_from_email,
        )
        result = self.email_provider.send(payload)
        lead = self._get_delivery_lead(delivery)

        if result.success:
            delivery.status = NOTIFICATION_STATUS_SENT
            delivery.sent_at = utc_now()
            delivery.error_message = None
            if lead is not None:
                LeadWorkflowService(self.session).mark_notified(lead)
        else:
            delivery.error_message = result.error_message or "Email provider failed"
            if delivery.attempts >= delivery.max_attempts:
                delivery.status = NOTIFICATION_STATUS_FAILED
                if lead is not None:
                    lead.notification_status = NOTIFICATION_STATUS_FAILED
            else:
                delivery.status = NOTIFICATION_STATUS_RETRY_SCHEDULED
                delivery.next_attempt_at = utc_now()
                if lead is not None:
                    lead.notification_status = NOTIFICATION_STATUS_RETRY_SCHEDULED

        self.session.flush()
        return delivery

    def resolve_recipient_email(self, tenant_id: str) -> str | None:
        """Resolve the current tenant's preferred notification email."""
        settings = self.session.scalars(
            select(BusinessNotificationSetting).where(
                BusinessNotificationSetting.tenant_id == tenant_id
            )
        ).first()
        if settings is not None:
            if not settings.lead_notifications_enabled:
                return None
            if settings.notification_email:
                return settings.notification_email

        statement = (
            select(Business.email)
            .where(Business.tenant_id == tenant_id, Business.email.is_not(None))
            .order_by(Business.created_at)
        )
        return self.session.scalar(statement)

    def _get_delivery_lead(self, delivery: NotificationDelivery) -> Lead | None:
        if delivery.lead_id is None:
            return None
        statement = select(Lead).where(
            Lead.id == delivery.lead_id,
            Lead.tenant_id == delivery.tenant_id,
        )
        return self.session.scalars(statement).first()
