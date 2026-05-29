"""Super admin data access services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.analytics.service import AnalyticsService
from app.core.config import Settings, get_settings
from app.core.passwords import hash_password
from app.db.base import utc_now
from app.models.billing import TenantSubscription
from app.models.conversation import Conversation, Message
from app.models.knowledge import DocumentChunk, KnowledgeDocument
from app.models.lead import Lead
from app.models.notification import BusinessNotificationSetting, NotificationDelivery
from app.models.tenant import Business, BusinessUser, Tenant
from app.models.usage import AuditLog, GlobalAuditLog, UsageLog
from app.models.widget import WidgetConfig


@dataclass(frozen=True)
class TenantMetrics:
    """Compact tenant metrics for admin views."""

    businesses_total: int
    users_total: int
    documents_total: int
    leads_total: int
    conversations_total: int
    messages_total: int
    usage_events_total: int


class AdminService:
    """Read and manage platform data through super admin workflows."""

    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()

    def list_tenants(self) -> list[Tenant]:
        statement = select(Tenant).order_by(Tenant.created_at.desc())
        return list(self.session.scalars(statement))

    def get_tenant(self, tenant_id: str) -> Tenant | None:
        return self.session.get(Tenant, tenant_id)

    def create_tenant(
        self,
        *,
        name: str,
        slug: str,
        status: str = "active",
        business_name: str | None = None,
        business_email: str | None = None,
        owner_email: str | None = None,
        owner_password: str | None = None,
    ) -> Tenant:
        tenant = Tenant(name=name, slug=slug, status=status)
        self.session.add(tenant)
        self.session.flush()
        business = Business(
            tenant_id=tenant.id,
            name=business_name or name,
            email=business_email,
        )
        self.session.add(business)
        self.session.flush()
        if owner_email:
            self.session.add(
                BusinessUser(
                    tenant_id=tenant.id,
                    business_id=business.id,
                    email=owner_email,
                    full_name=f"{name} Owner",
                    role="owner",
                    status="active",
                    password_hash=hash_password(owner_password)
                    if owner_password
                    else None,
                    password_updated_at=utc_now() if owner_password else None,
                )
            )
            self.session.flush()
        return tenant

    def update_tenant_status(self, tenant_id: str, status: str) -> Tenant | None:
        tenant = self.get_tenant(tenant_id)
        if tenant is None:
            return None
        tenant.status = status
        self.session.flush()
        return tenant

    def offboard_tenant(self, tenant_id: str, retention_days: int | None = None) -> Tenant | None:
        """Mark a tenant for offboarding and calculate the retention deadline."""
        tenant = self.get_tenant(tenant_id)
        if tenant is None:
            return None
        retention = retention_days or self.settings.privacy_default_retention_days
        now = utc_now()
        tenant.status = "offboarding"
        tenant.offboarded_at = now
        tenant.deletion_requested_at = now
        tenant.data_retention_until = now + timedelta(days=retention)
        self.session.flush()
        return tenant

    def export_tenant_data(self, tenant_id: str) -> dict[str, Any] | None:
        """Return a beta-scope tenant data export without password hashes or embeddings."""
        tenant = self.get_tenant(tenant_id)
        if tenant is None:
            return None
        documents = self._tenant_rows(KnowledgeDocument, tenant_id)
        document_ids = [document.id for document in documents]
        messages = self._tenant_rows(Message, tenant_id)
        conversations = self._tenant_rows(Conversation, tenant_id)
        leads = self._tenant_rows(Lead, tenant_id)
        return {
            "generated_at": utc_now().isoformat(),
            "tenant": {
                "id": tenant.id,
                "name": tenant.name,
                "slug": tenant.slug,
                "status": tenant.status,
                "offboarded_at": isoformat_or_none(tenant.offboarded_at),
                "deletion_requested_at": isoformat_or_none(tenant.deletion_requested_at),
                "data_retention_until": isoformat_or_none(tenant.data_retention_until),
                "created_at": isoformat_or_none(tenant.created_at),
                "updated_at": isoformat_or_none(tenant.updated_at),
            },
            "businesses": [business_export(business) for business in self.list_businesses(tenant_id)],
            "business_users": [
                business_user_export(user) for user in self.list_business_users(tenant_id)
            ],
            "documents": [document_export(document) for document in documents],
            "document_chunks": [
                document_chunk_export(chunk)
                for chunk in self._tenant_rows(DocumentChunk, tenant_id)
                if chunk.document_id in document_ids
            ],
            "conversations": [
                conversation_export(conversation) for conversation in conversations
            ],
            "messages": [message_export(message) for message in messages],
            "leads": [lead_export(lead) for lead in leads],
            "notification_settings": [
                notification_setting_export(setting)
                for setting in self._tenant_rows(BusinessNotificationSetting, tenant_id)
            ],
            "notification_deliveries": [
                notification_delivery_export(delivery)
                for delivery in self._tenant_rows(NotificationDelivery, tenant_id)
            ],
            "usage_logs": [usage_log_export(event) for event in self.recent_usage(tenant_id, 500)],
            "audit_logs": [
                audit_log_export(event)
                for event in self._tenant_rows(AuditLog, tenant_id, limit=500)
            ],
            "widget_configs": [
                widget_config_export(widget)
                for widget in self._tenant_rows(WidgetConfig, tenant_id)
            ],
            "subscriptions": [
                subscription_export(subscription)
                for subscription in self._tenant_rows(TenantSubscription, tenant_id)
            ],
        }

    def delete_tenant_data(self, tenant_id: str, confirm_slug: str) -> Tenant | None:
        """Delete tenant-owned beta data after an explicit slug confirmation."""
        tenant = self.get_tenant(tenant_id)
        if tenant is None:
            return None
        if tenant.slug != confirm_slug:
            raise ValueError("Tenant slug confirmation does not match")
        self._delete_tenant_children(tenant_id)
        self.session.delete(tenant)
        self.session.flush()
        return tenant

    def list_businesses(self, tenant_id: str) -> list[Business]:
        statement = (
            select(Business)
            .where(Business.tenant_id == tenant_id)
            .order_by(Business.created_at)
        )
        return list(self.session.scalars(statement))

    def list_business_users(self, tenant_id: str) -> list[BusinessUser]:
        statement = (
            select(BusinessUser)
            .where(BusinessUser.tenant_id == tenant_id)
            .order_by(BusinessUser.created_at)
        )
        return list(self.session.scalars(statement))

    def tenant_metrics(self, tenant_id: str) -> TenantMetrics:
        return TenantMetrics(
            businesses_total=self._tenant_count(Business, tenant_id),
            users_total=self._tenant_count(BusinessUser, tenant_id),
            documents_total=self._tenant_count(KnowledgeDocument, tenant_id),
            leads_total=self._tenant_count(Lead, tenant_id),
            conversations_total=self._tenant_count(Conversation, tenant_id),
            messages_total=self._tenant_count(Message, tenant_id),
            usage_events_total=self._tenant_count(UsageLog, tenant_id),
        )

    def usage_overview(self):
        return AnalyticsService(self.session, self.settings).platform_snapshot()

    def recent_leads(self, tenant_id: str, limit: int = 10) -> list[Lead]:
        statement = (
            select(Lead)
            .where(Lead.tenant_id == tenant_id)
            .order_by(Lead.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def recent_conversations(self, tenant_id: str, limit: int = 10) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(Conversation.tenant_id == tenant_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def recent_usage(self, tenant_id: str, limit: int = 10) -> list[UsageLog]:
        statement = (
            select(UsageLog)
            .where(UsageLog.tenant_id == tenant_id)
            .order_by(UsageLog.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def recent_audit_logs(self, limit: int = 25) -> list[AuditLog | GlobalAuditLog]:
        tenant_statement = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        global_statement = (
            select(GlobalAuditLog).order_by(GlobalAuditLog.created_at.desc()).limit(limit)
        )
        events: list[AuditLog | GlobalAuditLog] = [
            *self.session.scalars(tenant_statement),
            *self.session.scalars(global_statement),
        ]
        events.sort(key=lambda event: event.created_at, reverse=True)
        return events[:limit]

    def message_count(self, conversation_id: str, tenant_id: str) -> int:
        statement = select(func.count()).select_from(Message).where(
            Message.conversation_id == conversation_id,
            Message.tenant_id == tenant_id,
        )
        return int(self.session.scalar(statement) or 0)

    def _tenant_count(self, model: type, tenant_id: str) -> int:
        statement = select(func.count()).select_from(model).where(model.tenant_id == tenant_id)
        return int(self.session.scalar(statement) or 0)

    def _tenant_rows(self, model: type, tenant_id: str, limit: int | None = None) -> list:
        statement = select(model).where(model.tenant_id == tenant_id).order_by(model.created_at)
        if limit:
            statement = statement.limit(limit)
        return list(self.session.scalars(statement))

    def _delete_tenant_children(self, tenant_id: str) -> None:
        for model in (
            NotificationDelivery,
            BusinessNotificationSetting,
            DocumentChunk,
            KnowledgeDocument,
            Message,
            Lead,
            Conversation,
            UsageLog,
            AuditLog,
            WidgetConfig,
            TenantSubscription,
            BusinessUser,
            Business,
        ):
            self.session.execute(delete(model).where(model.tenant_id == tenant_id))


def isoformat_or_none(value) -> str | None:
    return value.isoformat() if value else None


def business_export(business: Business) -> dict[str, Any]:
    return {
        "id": business.id,
        "name": business.name,
        "email": business.email,
        "phone": business.phone,
        "website_url": business.website_url,
        "created_at": isoformat_or_none(business.created_at),
    }


def business_user_export(user: BusinessUser) -> dict[str, Any]:
    return {
        "id": user.id,
        "business_id": user.business_id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "status": user.status,
        "last_login_at": isoformat_or_none(user.last_login_at),
        "created_at": isoformat_or_none(user.created_at),
    }


def document_export(document: KnowledgeDocument) -> dict[str, Any]:
    return {
        "id": document.id,
        "filename": document.filename,
        "content_type": document.content_type,
        "storage_path": document.storage_path,
        "status": document.status,
        "error_message": document.error_message,
        "created_at": isoformat_or_none(document.created_at),
    }


def document_chunk_export(chunk) -> dict[str, Any]:
    return {
        "id": chunk.id,
        "document_id": chunk.document_id,
        "chunk_index": chunk.chunk_index,
        "content": chunk.content,
        "token_count": chunk.token_count,
        "created_at": isoformat_or_none(chunk.created_at),
    }


def conversation_export(conversation: Conversation) -> dict[str, Any]:
    return {
        "id": conversation.id,
        "visitor_label": conversation.visitor_label,
        "status": conversation.status,
        "source": conversation.source,
        "created_at": isoformat_or_none(conversation.created_at),
    }


def message_export(message: Message) -> dict[str, Any]:
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "sender_type": message.sender_type,
        "content": message.content,
        "created_at": isoformat_or_none(message.created_at),
    }


def lead_export(lead: Lead) -> dict[str, Any]:
    return {
        "id": lead.id,
        "conversation_id": lead.conversation_id,
        "customer_name": lead.customer_name,
        "customer_email": lead.customer_email,
        "customer_phone": lead.customer_phone,
        "job_type": lead.job_type,
        "suburb": lead.suburb,
        "urgency": lead.urgency,
        "status": lead.status,
        "notification_status": lead.notification_status,
        "notes": lead.notes,
        "created_at": isoformat_or_none(lead.created_at),
    }


def notification_setting_export(setting: BusinessNotificationSetting) -> dict[str, Any]:
    return {
        "id": setting.id,
        "business_id": setting.business_id,
        "notification_email": setting.notification_email,
        "lead_notifications_enabled": setting.lead_notifications_enabled,
        "created_at": isoformat_or_none(setting.created_at),
    }


def notification_delivery_export(delivery: NotificationDelivery) -> dict[str, Any]:
    return {
        "id": delivery.id,
        "lead_id": delivery.lead_id,
        "notification_type": delivery.notification_type,
        "recipient_email": delivery.recipient_email,
        "subject": delivery.subject,
        "status": delivery.status,
        "attempts": delivery.attempts,
        "sent_at": isoformat_or_none(delivery.sent_at),
        "created_at": isoformat_or_none(delivery.created_at),
    }


def usage_log_export(event: UsageLog) -> dict[str, Any]:
    return {
        "id": event.id,
        "event_type": event.event_type,
        "event_source": event.event_source,
        "attributes": event.attributes or {},
        "created_at": isoformat_or_none(event.created_at),
    }


def audit_log_export(event: AuditLog) -> dict[str, Any]:
    return {
        "id": event.id,
        "actor_id": event.actor_id,
        "action": event.action,
        "target_type": event.target_type,
        "target_id": event.target_id,
        "attributes": event.attributes or {},
        "created_at": isoformat_or_none(event.created_at),
    }


def widget_config_export(widget: WidgetConfig) -> dict[str, Any]:
    return {
        "id": widget.id,
        "key_prefix": widget.key_prefix,
        "name": widget.name,
        "status": widget.status,
        "allowed_origins": widget.allowed_origins,
        "created_at": isoformat_or_none(widget.created_at),
    }


def subscription_export(subscription: TenantSubscription) -> dict[str, Any]:
    return {
        "id": subscription.id,
        "plan_code": subscription.plan_code,
        "plan_name": subscription.plan_name,
        "status": subscription.status,
        "billing_mode": subscription.billing_mode,
        "currency": subscription.currency,
        "monthly_price_cents": subscription.monthly_price_cents,
        "support_level": subscription.support_level,
        "trial_ends_at": isoformat_or_none(subscription.trial_ends_at),
        "current_period_ends_at": isoformat_or_none(subscription.current_period_ends_at),
        "canceled_at": isoformat_or_none(subscription.canceled_at),
        "created_at": isoformat_or_none(subscription.created_at),
        "updated_at": isoformat_or_none(subscription.updated_at),
    }
