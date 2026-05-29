"""Manual paid-beta billing entitlement service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import utc_now
from app.models.billing import TenantSubscription
from app.models.tenant import Tenant


BILLING_MODE_MANUAL = "manual"
SUBSCRIPTION_STATUSES = {"trialing", "active", "past_due", "paused", "canceled"}
SUBSCRIPTION_ACCESS_ALLOWED_STATUSES = {"trialing", "active"}


@dataclass(frozen=True)
class BillingPlan:
    """Code-defined beta plan with enforceable server-side limits."""

    code: str
    name: str
    description: str
    monthly_price_cents: int
    currency: str
    support_level: str
    trial_days: int
    chat_conversations_limit: int
    ai_responses_limit: int
    tokens_limit: int
    monthly_budget_cents: float
    documents_limit: int
    storage_mb_limit: int
    pages_crawled_limit: int


PLAN_CATALOG: tuple[BillingPlan, ...] = (
    BillingPlan(
        code="pilot_trial",
        name="Pilot Trial",
        description="Controlled no-card pilot for one approved beta business.",
        monthly_price_cents=0,
        currency="AUD",
        support_level="pilot",
        trial_days=30,
        chat_conversations_limit=300,
        ai_responses_limit=1000,
        tokens_limit=150000,
        monthly_budget_cents=1500,
        documents_limit=30,
        storage_mb_limit=256,
        pages_crawled_limit=250,
    ),
    BillingPlan(
        code="starter_manual",
        name="Starter Manual",
        description="Manually invoiced starter plan for early paid beta tenants.",
        monthly_price_cents=9900,
        currency="AUD",
        support_level="standard",
        trial_days=0,
        chat_conversations_limit=1000,
        ai_responses_limit=3000,
        tokens_limit=400000,
        monthly_budget_cents=4000,
        documents_limit=75,
        storage_mb_limit=512,
        pages_crawled_limit=750,
    ),
    BillingPlan(
        code="growth_manual",
        name="Growth Manual",
        description="Manually invoiced higher-limit beta plan with priority support.",
        monthly_price_cents=19900,
        currency="AUD",
        support_level="priority",
        trial_days=0,
        chat_conversations_limit=3000,
        ai_responses_limit=9000,
        tokens_limit=1200000,
        monthly_budget_cents=12000,
        documents_limit=200,
        storage_mb_limit=1024,
        pages_crawled_limit=2000,
    ),
)


class BillingService:
    """Manage manual paid-beta subscriptions and derived entitlements."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def plan_catalog(self) -> list[BillingPlan]:
        """Return available beta plans."""
        return list(PLAN_CATALOG)

    def get_plan(self, plan_code: str) -> BillingPlan | None:
        """Return one plan by code."""
        return next((plan for plan in PLAN_CATALOG if plan.code == plan_code), None)

    def get_subscription(self, tenant_id: str) -> TenantSubscription | None:
        """Return one tenant subscription without crossing tenant boundaries."""
        return self.session.scalars(
            select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id)
        ).first()

    def tenant_exists(self, tenant_id: str) -> bool:
        """Return whether a tenant exists."""
        return bool(
            self.session.scalar(select(Tenant.id).where(Tenant.id == tenant_id))
        )

    def set_manual_subscription(
        self,
        *,
        tenant_id: str,
        plan_code: str,
        status: str,
        admin_id: str,
        billing_contact_email: str | None = None,
        manual_reference: str | None = None,
        notes: str | None = None,
    ) -> TenantSubscription:
        """Create or update a tenant subscription from the manual beta catalog."""
        if status not in SUBSCRIPTION_STATUSES:
            raise ValueError("Unsupported subscription status")
        plan = self.get_plan(plan_code)
        if plan is None:
            raise ValueError("Unsupported billing plan")
        if not self.tenant_exists(tenant_id):
            raise LookupError("Tenant not found")

        subscription = self.get_subscription(tenant_id)
        now = utc_now()
        if subscription is None:
            subscription = TenantSubscription(
                tenant_id=tenant_id,
                plan_code=plan.code,
                plan_name=plan.name,
                status=status,
                billing_mode=BILLING_MODE_MANUAL,
                currency=plan.currency,
                monthly_price_cents=plan.monthly_price_cents,
                support_level=plan.support_level,
                chat_conversations_limit=plan.chat_conversations_limit,
                ai_responses_limit=plan.ai_responses_limit,
                tokens_limit=plan.tokens_limit,
                monthly_budget_cents=plan.monthly_budget_cents,
                documents_limit=plan.documents_limit,
                storage_mb_limit=plan.storage_mb_limit,
                pages_crawled_limit=plan.pages_crawled_limit,
                current_period_starts_at=now,
                current_period_ends_at=now + timedelta(days=30),
            )
            self.session.add(subscription)

        self._apply_plan(subscription, plan)
        subscription.status = status
        subscription.billing_mode = BILLING_MODE_MANUAL
        subscription.billing_contact_email = clean_optional(billing_contact_email)
        subscription.manual_reference = clean_optional(manual_reference)
        subscription.notes = clean_optional(notes)
        subscription.updated_by_admin_id = admin_id

        if status == "trialing":
            subscription.trial_started_at = subscription.trial_started_at or now
            subscription.trial_ends_at = now + timedelta(days=max(plan.trial_days, 1))
            subscription.current_period_starts_at = now
            subscription.current_period_ends_at = subscription.trial_ends_at
            subscription.canceled_at = None
        elif status == "active":
            subscription.current_period_starts_at = now
            subscription.current_period_ends_at = now + timedelta(days=30)
            subscription.canceled_at = None
        elif status == "canceled":
            subscription.canceled_at = now
        elif status in {"paused", "past_due"}:
            subscription.canceled_at = None

        self.session.flush()
        return subscription

    def _apply_plan(
        self,
        subscription: TenantSubscription,
        plan: BillingPlan,
    ) -> None:
        subscription.plan_code = plan.code
        subscription.plan_name = plan.name
        subscription.currency = plan.currency
        subscription.monthly_price_cents = plan.monthly_price_cents
        subscription.support_level = plan.support_level
        subscription.chat_conversations_limit = plan.chat_conversations_limit
        subscription.ai_responses_limit = plan.ai_responses_limit
        subscription.tokens_limit = plan.tokens_limit
        subscription.monthly_budget_cents = plan.monthly_budget_cents
        subscription.documents_limit = plan.documents_limit
        subscription.storage_mb_limit = plan.storage_mb_limit
        subscription.pages_crawled_limit = plan.pages_crawled_limit


def clean_optional(value: str | None) -> str | None:
    """Trim optional billing fields and store empty strings as null."""
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None
