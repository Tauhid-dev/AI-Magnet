"""Tenant usage metering, quota snapshots, and limit enforcement."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.billing import SUBSCRIPTION_ACCESS_ALLOWED_STATUSES
from app.core.config import Settings, get_settings
from app.db.base import utc_now
from app.models.billing import TenantSubscription
from app.models.conversation import Conversation
from app.models.knowledge import KnowledgeDocument, WebsiteCrawlPage
from app.models.usage import UsageLog
from app.usage.service import UsageService
from app.usage.taxonomy import UsageEventSource, UsageEventType


@dataclass(frozen=True)
class QuotaMetric:
    """One measured tenant quota/cost signal."""

    key: str
    label: str
    used: float
    limit: float
    unit: str
    percent_used: float
    warning: bool
    blocked: bool


@dataclass(frozen=True)
class QuotaSnapshot:
    """Current tenant quota state for the active monthly window."""

    tenant_id: str
    period_start: datetime
    period_end: datetime
    warning_threshold_percent: float
    metrics: list[QuotaMetric]
    warnings: list[str]
    blocked_reasons: list[str]


@dataclass(frozen=True)
class QuotaLimits:
    """Effective tenant limits from paid-beta entitlements or defaults."""

    chat_conversations_per_month: int
    ai_responses_per_month: int
    tokens_per_month: int
    monthly_budget_cents: float
    documents_total: int
    storage_mb: int
    pages_crawled_per_month: int


class QuotaLimitExceeded(RuntimeError):
    """Raised when a tenant operation is blocked by configured quota limits."""

    def __init__(self, operation: str, blocked_reasons: list[str]) -> None:
        self.operation = operation
        self.blocked_reasons = blocked_reasons
        super().__init__(f"{operation} quota exceeded: {', '.join(blocked_reasons)}")


def month_bounds(now: datetime | None = None) -> tuple[datetime, datetime]:
    """Return UTC start/end datetimes for the current calendar month."""
    current = now or utc_now()
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    start = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


def estimate_ai_cost_cents(
    prompt_tokens: int,
    completion_tokens: int,
    settings: Settings,
) -> float:
    """Estimate provider cost in cents from configured per-1K token prices."""
    prompt_cost = (max(prompt_tokens, 0) / 1000) * settings.ai_prompt_cost_cents_per_1k_tokens
    completion_cost = (
        max(completion_tokens, 0) / 1000
    ) * settings.ai_completion_cost_cents_per_1k_tokens
    return round(prompt_cost + completion_cost, 6)


class QuotaService:
    """Compute tenant quota/cost state from existing tenant-scoped usage data."""

    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()

    def snapshot(self, tenant_id: str, now: datetime | None = None) -> QuotaSnapshot:
        """Return a quota snapshot for one tenant without reading other tenant data."""
        period_start, period_end = month_bounds(now)
        limits = self._effective_limits(tenant_id)
        monthly_events = self._monthly_events(tenant_id, period_start, period_end)
        documents_total = self._documents_total(tenant_id)
        storage_bytes = self._storage_bytes(tenant_id)
        pages_crawled = self._pages_crawled(tenant_id, period_start, period_end)
        total_tokens = self._estimated_tokens(monthly_events)
        estimated_cost = self._estimated_cost(monthly_events)
        metrics = [
            self._metric(
                key="chat_conversations",
                label="Chat conversations",
                used=self._conversation_count(tenant_id, period_start, period_end),
                limit=limits.chat_conversations_per_month,
                unit="conversations/month",
            ),
            self._metric(
                key="ai_responses",
                label="AI responses",
                used=self._event_count(
                    monthly_events,
                    UsageEventType.ASSISTANT_RESPONSE_GENERATED,
                )
                + self._event_count(monthly_events, UsageEventType.AGENT_SANDBOX_TESTED),
                limit=limits.ai_responses_per_month,
                unit="responses/month",
            ),
            self._metric(
                key="estimated_tokens",
                label="Estimated AI tokens",
                used=total_tokens,
                limit=limits.tokens_per_month,
                unit="tokens/month",
            ),
            self._metric(
                key="estimated_cost_cents",
                label="Estimated AI cost",
                used=estimated_cost,
                limit=limits.monthly_budget_cents,
                unit="cents/month",
            ),
            self._metric(
                key="documents_total",
                label="Knowledge documents",
                used=documents_total,
                limit=limits.documents_total,
                unit="documents",
            ),
            self._metric(
                key="storage_mb",
                label="Knowledge storage",
                used=round(storage_bytes / 1024 / 1024, 4),
                limit=limits.storage_mb,
                unit="MB",
            ),
            self._metric(
                key="pages_crawled",
                label="Pages crawled",
                used=pages_crawled,
                limit=limits.pages_crawled_per_month,
                unit="pages/month",
            ),
            self._metric(
                key="rate_limit_events",
                label="Rate limit events",
                used=self._event_count(monthly_events, UsageEventType.RATE_LIMIT_EXCEEDED),
                limit=max(self.settings.rate_limit_chat_message_per_minute, 1) * 60,
                unit="events/month",
                enforce=False,
            ),
        ]
        warnings = [metric.label for metric in metrics if metric.warning]
        blocked_reasons = [
            *[metric.label for metric in metrics if metric.blocked],
            *self.subscription_blockers(tenant_id),
        ]
        return QuotaSnapshot(
            tenant_id=tenant_id,
            period_start=period_start,
            period_end=period_end,
            warning_threshold_percent=self.settings.quota_warning_threshold_percent,
            metrics=metrics,
            warnings=warnings,
            blocked_reasons=blocked_reasons,
        )

    def chat_start_blockers(self, tenant_id: str) -> list[str]:
        """Return blocking reasons before starting a new widget conversation."""
        return self._blocking_reasons(tenant_id, {"chat_conversations"})

    def ai_response_blockers(self, tenant_id: str) -> list[str]:
        """Return blocking reasons before generating a billable AI response."""
        return self._blocking_reasons(
            tenant_id,
            {"ai_responses", "estimated_tokens", "estimated_cost_cents"},
        )

    def document_blockers(self, tenant_id: str, additional_storage_bytes: int = 0) -> list[str]:
        """Return blocking reasons before accepting more tenant knowledge."""
        snapshot = self.snapshot(tenant_id)
        blockers = [
            metric.label
            for metric in snapshot.metrics
            if metric.blocked and metric.key in {"documents_total", "storage_mb"}
        ]
        blockers.extend(self.subscription_blockers(tenant_id))
        if additional_storage_bytes > 0:
            storage_limit_bytes = self._effective_limits(tenant_id).storage_mb * 1024 * 1024
            if self._storage_bytes(tenant_id) + additional_storage_bytes > storage_limit_bytes:
                blockers.append("Knowledge storage")
        return sorted(set(blockers))

    def website_crawl_blockers(self, tenant_id: str) -> list[str]:
        """Return blocking reasons before queuing a website crawl/refresh."""
        return self._blocking_reasons(tenant_id, {"pages_crawled"})

    def record_quota_block(
        self,
        *,
        tenant_id: str,
        operation: str,
        blocked_reasons: list[str],
    ) -> None:
        """Record a non-PII quota block event for operations analytics."""
        UsageService(self.session).record_event(
            tenant_id=tenant_id,
            event_type=UsageEventType.QUOTA_LIMIT_EXCEEDED,
            event_source=UsageEventSource.OPERATIONS,
            attributes={"operation": operation, "blocked_reasons": blocked_reasons},
        )

    def subscription_blockers(self, tenant_id: str) -> list[str]:
        """Return subscription state blockers for manually paid beta tenants."""
        subscription = self._subscription(tenant_id)
        if subscription is None:
            return []
        if (
            subscription.status == "trialing"
            and subscription.trial_ends_at is not None
            and subscription.trial_ends_at < utc_now()
        ):
            return ["Subscription trial expired"]
        if subscription.status in SUBSCRIPTION_ACCESS_ALLOWED_STATUSES:
            return []
        return [f"Subscription {subscription.status.replace('_', ' ')}"]

    def _blocking_reasons(self, tenant_id: str, keys: set[str]) -> list[str]:
        snapshot = self.snapshot(tenant_id)
        return [
            metric.label
            for metric in snapshot.metrics
            if metric.key in keys and metric.blocked
        ] + self.subscription_blockers(tenant_id)

    def _effective_limits(self, tenant_id: str) -> QuotaLimits:
        subscription = self._subscription(tenant_id)
        if subscription is not None:
            return QuotaLimits(
                chat_conversations_per_month=subscription.chat_conversations_limit,
                ai_responses_per_month=subscription.ai_responses_limit,
                tokens_per_month=subscription.tokens_limit,
                monthly_budget_cents=subscription.monthly_budget_cents,
                documents_total=subscription.documents_limit,
                storage_mb=subscription.storage_mb_limit,
                pages_crawled_per_month=subscription.pages_crawled_limit,
            )
        return QuotaLimits(
            chat_conversations_per_month=self.settings.tenant_quota_chat_conversations_per_month,
            ai_responses_per_month=self.settings.tenant_quota_ai_responses_per_month,
            tokens_per_month=self.settings.tenant_quota_tokens_per_month,
            monthly_budget_cents=self.settings.tenant_budget_monthly_cents,
            documents_total=self.settings.tenant_quota_documents_total,
            storage_mb=self.settings.tenant_quota_storage_mb,
            pages_crawled_per_month=self.settings.tenant_quota_pages_crawled_per_month,
        )

    def _subscription(self, tenant_id: str) -> TenantSubscription | None:
        return self.session.scalars(
            select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id)
        ).first()

    def _metric(
        self,
        *,
        key: str,
        label: str,
        used: float,
        limit: float,
        unit: str,
        enforce: bool = True,
    ) -> QuotaMetric:
        percent = round((used / limit) * 100, 2) if limit > 0 else 0.0
        warning = limit > 0 and percent >= self.settings.quota_warning_threshold_percent
        blocked = enforce and limit > 0 and used >= limit
        return QuotaMetric(
            key=key,
            label=label,
            used=round(used, 6),
            limit=limit,
            unit=unit,
            percent_used=percent,
            warning=warning,
            blocked=blocked,
        )

    def _monthly_events(
        self,
        tenant_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> list[UsageLog]:
        statement = (
            select(UsageLog)
            .where(
                UsageLog.tenant_id == tenant_id,
                UsageLog.created_at >= period_start,
                UsageLog.created_at < period_end,
            )
            .order_by(UsageLog.created_at)
        )
        return list(self.session.scalars(statement))

    def _conversation_count(
        self,
        tenant_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> int:
        return int(
            self.session.scalar(
                select(func.count(Conversation.id)).where(
                    Conversation.tenant_id == tenant_id,
                    Conversation.created_at >= period_start,
                    Conversation.created_at < period_end,
                )
            )
            or 0
        )

    def _documents_total(self, tenant_id: str) -> int:
        return int(
            self.session.scalar(
                select(func.count(KnowledgeDocument.id)).where(
                    KnowledgeDocument.tenant_id == tenant_id
                )
            )
            or 0
        )

    def _storage_bytes(self, tenant_id: str) -> int:
        return int(
            self.session.scalar(
                select(func.coalesce(func.sum(KnowledgeDocument.file_size_bytes), 0)).where(
                    KnowledgeDocument.tenant_id == tenant_id
                )
            )
            or 0
        )

    def _pages_crawled(
        self,
        tenant_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> int:
        page_count = int(
            self.session.scalar(
                select(func.count(WebsiteCrawlPage.id)).where(
                    WebsiteCrawlPage.tenant_id == tenant_id,
                    WebsiteCrawlPage.status == "ingested",
                    WebsiteCrawlPage.crawled_at >= period_start,
                    WebsiteCrawlPage.crawled_at < period_end,
                )
            )
            or 0
        )
        if page_count:
            return page_count
        monthly_events = self._monthly_events(tenant_id, period_start, period_end)
        return int(self._sum_attrs(monthly_events, "pages_ingested"))

    def _sum_attrs(self, events: list[UsageLog], key: str) -> float:
        total = 0.0
        for event in events:
            value = (event.attributes or {}).get(key)
            if isinstance(value, int | float):
                total += float(value)
        return total

    def _event_count(self, events: list[UsageLog], event_type: str) -> int:
        return sum(1 for event in events if event.event_type == event_type)

    def _estimated_tokens(self, events: list[UsageLog]) -> int:
        total = 0
        for event in events:
            attrs = event.attributes or {}
            explicit_total = attrs.get("estimated_total_tokens")
            if isinstance(explicit_total, int | float) and explicit_total > 0:
                total += int(explicit_total)
                continue
            prompt_tokens = attrs.get("estimated_prompt_tokens")
            response_tokens = attrs.get("estimated_response_tokens")
            total += int(prompt_tokens) if isinstance(prompt_tokens, int | float) else 0
            total += int(response_tokens) if isinstance(response_tokens, int | float) else 0
        return total

    def _estimated_cost(self, events: list[UsageLog]) -> float:
        total = 0.0
        for event in events:
            attrs = event.attributes or {}
            explicit_cost = attrs.get("estimated_cost_cents")
            if isinstance(explicit_cost, int | float):
                total += float(explicit_cost)
                continue
            prompt_tokens = attrs.get("estimated_prompt_tokens")
            response_tokens = attrs.get("estimated_response_tokens")
            total += estimate_ai_cost_cents(
                int(prompt_tokens) if isinstance(prompt_tokens, int | float) else 0,
                int(response_tokens) if isinstance(response_tokens, int | float) else 0,
                self.settings,
            )
        return round(total, 6)


def retry_after_for_month(now: datetime | None = None) -> int:
    """Return seconds until the next monthly quota window."""
    current = now or utc_now()
    _start, end = month_bounds(current)
    return max(60, ceil((end - current).total_seconds()))
