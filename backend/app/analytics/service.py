"""Tenant-scoped and platform analytics queries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.conversation import Conversation, Message
from app.models.knowledge import KnowledgeDocument
from app.models.lead import Lead
from app.models.notification import NotificationDelivery
from app.models.tenant import Tenant
from app.models.usage import AuditLog, GlobalAuditLog, UsageLog
from app.models.widget import WidgetConfig
from app.usage.quotas import QuotaService, QuotaSnapshot
from app.usage.taxonomy import UsageEventType


@dataclass(frozen=True)
class AnalyticsBreakdown:
    """One analytics label/count pair."""

    label: str
    count: int


@dataclass(frozen=True)
class AnalyticsUsageEvent:
    """Recent usage event with analytics-safe attributes."""

    event_type: str
    event_source: str | None
    attributes: dict[str, Any]
    created_at: datetime


@dataclass(frozen=True)
class TenantAnalyticsSnapshot:
    """Tenant-scoped analytics snapshot."""

    documents_total: int
    documents_ingested: int
    documents_failed: int
    leads_total: int
    leads_qualified: int
    leads_notified: int
    conversations_total: int
    open_conversations: int
    messages_total: int
    visitor_messages_total: int
    assistant_messages_total: int
    usage_events_total: int
    ai_responses_total: int
    lead_notifications_sent: int
    widget_status: str
    lead_status_counts: list[AnalyticsBreakdown]
    document_status_counts: list[AnalyticsBreakdown]
    usage_event_counts: list[AnalyticsBreakdown]
    recent_usage: list[AnalyticsUsageEvent]
    quota_status: QuotaSnapshot


@dataclass(frozen=True)
class AdminTenantUsageSummary:
    """Compact per-tenant usage summary for platform analytics."""

    tenant_id: str
    tenant_name: str
    tenant_slug: str
    tenant_status: str
    documents_total: int
    leads_total: int
    conversations_total: int
    messages_total: int
    usage_events_total: int
    estimated_tokens: int
    estimated_cost_cents: float
    quota_warnings: list[str]
    quota_blockers: list[str]


@dataclass(frozen=True)
class PlatformAnalyticsSnapshot:
    """Platform-wide analytics snapshot."""

    tenants_total: int
    active_tenants: int
    documents_total: int
    documents_ingested: int
    leads_total: int
    leads_qualified: int
    conversations_total: int
    messages_total: int
    usage_events_total: int
    ai_responses_total: int
    lead_notifications_sent: int
    admin_audit_events_total: int
    estimated_tokens_total: int
    estimated_cost_cents_total: float
    pages_crawled_total: int
    storage_mb_total: float
    rate_limit_events_total: int
    quota_warning_tenants: int
    quota_blocked_tenants: int
    usage_event_counts: list[AnalyticsBreakdown]
    lead_status_counts: list[AnalyticsBreakdown]
    document_status_counts: list[AnalyticsBreakdown]
    tenant_usage: list[AdminTenantUsageSummary]


class AnalyticsService:
    """Build analytics snapshots without crossing tenant boundaries."""

    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.quotas = QuotaService(session, self.settings)

    def tenant_snapshot(self, tenant_id: str) -> TenantAnalyticsSnapshot:
        """Return analytics for one tenant only."""
        widget = self._active_widget(tenant_id)
        return TenantAnalyticsSnapshot(
            documents_total=self._tenant_count(KnowledgeDocument, tenant_id),
            documents_ingested=self._tenant_count(
                KnowledgeDocument,
                tenant_id,
                KnowledgeDocument.status == "ingested",
            ),
            documents_failed=self._tenant_count(
                KnowledgeDocument,
                tenant_id,
                KnowledgeDocument.status == "failed",
            ),
            leads_total=self._tenant_count(Lead, tenant_id),
            leads_qualified=self._tenant_count(Lead, tenant_id, Lead.status == "qualified"),
            leads_notified=self._tenant_count(Lead, tenant_id, Lead.status == "notified"),
            conversations_total=self._tenant_count(Conversation, tenant_id),
            open_conversations=self._tenant_count(
                Conversation,
                tenant_id,
                Conversation.status == "open",
            ),
            messages_total=self._tenant_count(Message, tenant_id),
            visitor_messages_total=self._tenant_count(
                Message,
                tenant_id,
                Message.sender_type == "visitor",
            ),
            assistant_messages_total=self._tenant_count(
                Message,
                tenant_id,
                Message.sender_type == "assistant",
            ),
            usage_events_total=self._tenant_count(UsageLog, tenant_id),
            ai_responses_total=self._tenant_count(
                UsageLog,
                tenant_id,
                UsageLog.event_type == UsageEventType.ASSISTANT_RESPONSE_GENERATED,
            ),
            lead_notifications_sent=self._tenant_count(
                NotificationDelivery,
                tenant_id,
                NotificationDelivery.status == "sent",
            ),
            widget_status=widget.status if widget else "not_configured",
            lead_status_counts=self._tenant_breakdown(Lead, tenant_id, Lead.status),
            document_status_counts=self._tenant_breakdown(
                KnowledgeDocument,
                tenant_id,
                KnowledgeDocument.status,
            ),
            usage_event_counts=self._tenant_breakdown(UsageLog, tenant_id, UsageLog.event_type),
            recent_usage=self._recent_usage(tenant_id),
            quota_status=self.quotas.snapshot(tenant_id),
        )

    def platform_snapshot(self, tenant_limit: int = 20) -> PlatformAnalyticsSnapshot:
        """Return platform-wide aggregate analytics for super admins."""
        tenant_usage = self._tenant_usage_summaries(tenant_limit)
        return PlatformAnalyticsSnapshot(
            tenants_total=self._count(Tenant),
            active_tenants=self._count(Tenant, Tenant.status == "active"),
            documents_total=self._count(KnowledgeDocument),
            documents_ingested=self._count(
                KnowledgeDocument,
                KnowledgeDocument.status == "ingested",
            ),
            leads_total=self._count(Lead),
            leads_qualified=self._count(Lead, Lead.status == "qualified"),
            conversations_total=self._count(Conversation),
            messages_total=self._count(Message),
            usage_events_total=self._count(UsageLog),
            ai_responses_total=self._count(
                UsageLog,
                UsageLog.event_type == UsageEventType.ASSISTANT_RESPONSE_GENERATED,
            ),
            lead_notifications_sent=self._count(
                NotificationDelivery,
                NotificationDelivery.status == "sent",
            ),
            admin_audit_events_total=self._count(AuditLog),
            estimated_tokens_total=sum(item.estimated_tokens for item in tenant_usage),
            estimated_cost_cents_total=round(
                sum(item.estimated_cost_cents for item in tenant_usage),
                6,
            ),
            pages_crawled_total=int(
                sum(self._metric_used(item.tenant_id, "pages_crawled") for item in tenant_usage)
            ),
            storage_mb_total=round(
                sum(self._metric_used(item.tenant_id, "storage_mb") for item in tenant_usage),
                4,
            ),
            rate_limit_events_total=self._rate_limit_events_total(),
            quota_warning_tenants=sum(1 for item in tenant_usage if item.quota_warnings),
            quota_blocked_tenants=sum(1 for item in tenant_usage if item.quota_blockers),
            usage_event_counts=self._breakdown(UsageLog, UsageLog.event_type),
            lead_status_counts=self._breakdown(Lead, Lead.status),
            document_status_counts=self._breakdown(KnowledgeDocument, KnowledgeDocument.status),
            tenant_usage=tenant_usage,
        )

    def _active_widget(self, tenant_id: str) -> WidgetConfig | None:
        statement = (
            select(WidgetConfig)
            .where(
                WidgetConfig.tenant_id == tenant_id,
                WidgetConfig.status == "active",
            )
            .order_by(WidgetConfig.created_at.desc())
        )
        return self.session.scalars(statement).first()

    def _recent_usage(self, tenant_id: str, limit: int = 10) -> list[AnalyticsUsageEvent]:
        statement = (
            select(UsageLog)
            .where(UsageLog.tenant_id == tenant_id)
            .order_by(UsageLog.created_at.desc())
            .limit(limit)
        )
        return [
            AnalyticsUsageEvent(
                event_type=event.event_type,
                event_source=event.event_source,
                attributes=event.attributes or {},
                created_at=event.created_at,
            )
            for event in self.session.scalars(statement)
        ]

    def _tenant_usage_summaries(self, limit: int) -> list[AdminTenantUsageSummary]:
        tenants = list(
            self.session.scalars(select(Tenant).order_by(Tenant.created_at.desc()).limit(limit))
        )
        summaries: list[AdminTenantUsageSummary] = []
        for tenant in tenants:
            quota_status = self.quotas.snapshot(tenant.id)
            summaries.append(
                AdminTenantUsageSummary(
                    tenant_id=tenant.id,
                    tenant_name=tenant.name,
                    tenant_slug=tenant.slug,
                    tenant_status=tenant.status,
                    documents_total=self._tenant_count(KnowledgeDocument, tenant.id),
                    leads_total=self._tenant_count(Lead, tenant.id),
                    conversations_total=self._tenant_count(Conversation, tenant.id),
                    messages_total=self._tenant_count(Message, tenant.id),
                    usage_events_total=self._tenant_count(UsageLog, tenant.id),
                    estimated_tokens=int(
                        self._metric_used_from_snapshot(quota_status, "estimated_tokens")
                    ),
                    estimated_cost_cents=self._metric_used_from_snapshot(
                        quota_status,
                        "estimated_cost_cents",
                    ),
                    quota_warnings=quota_status.warnings,
                    quota_blockers=quota_status.blocked_reasons,
                )
            )
        return summaries

    def _metric_used(self, tenant_id: str, key: str) -> float:
        return self._metric_used_from_snapshot(self.quotas.snapshot(tenant_id), key)

    def _metric_used_from_snapshot(self, snapshot: QuotaSnapshot, key: str) -> float:
        for metric in snapshot.metrics:
            if metric.key == key:
                return metric.used
        return 0.0

    def _rate_limit_events_total(self) -> int:
        tenant_events = self._count(
            UsageLog,
            UsageLog.event_type == UsageEventType.RATE_LIMIT_EXCEEDED,
        )
        global_events = self._count(
            GlobalAuditLog,
            GlobalAuditLog.action == UsageEventType.RATE_LIMIT_EXCEEDED,
        )
        return tenant_events + global_events

    def _breakdown(self, model: type, column) -> list[AnalyticsBreakdown]:
        statement = (
            select(column, func.count())
            .select_from(model)
            .group_by(column)
            .order_by(func.count().desc())
        )
        return [
            AnalyticsBreakdown(label=str(label), count=int(count))
            for label, count in self.session.execute(statement)
        ]

    def _tenant_breakdown(self, model: type, tenant_id: str, column) -> list[AnalyticsBreakdown]:
        statement = (
            select(column, func.count())
            .select_from(model)
            .where(model.tenant_id == tenant_id)
            .group_by(column)
            .order_by(func.count().desc())
        )
        return [
            AnalyticsBreakdown(label=str(label), count=int(count))
            for label, count in self.session.execute(statement)
        ]

    def _count(self, model: type, *criteria) -> int:
        statement = select(func.count()).select_from(model)
        if criteria:
            statement = statement.where(*criteria)
        return int(self.session.scalar(statement) or 0)

    def _tenant_count(self, model: type, tenant_id: str, *criteria) -> int:
        statement = select(func.count()).select_from(model).where(model.tenant_id == tenant_id)
        if criteria:
            statement = statement.where(*criteria)
        return int(self.session.scalar(statement) or 0)
