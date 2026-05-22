"""Deterministic tenant-scoped lead lifecycle rules."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.base import utc_now
from app.models.lead import Lead


LEAD_STATUS_NEW = "new"
LEAD_STATUS_NEEDS_INFO = "needs_info"
LEAD_STATUS_QUALIFIED = "qualified"
LEAD_STATUS_NOTIFIED = "notified"
LEAD_STATUS_CONTACTED = "contacted"
LEAD_STATUS_CLOSED = "closed"
LEAD_STATUS_DISQUALIFIED = "disqualified"

LEAD_STATUSES = {
    LEAD_STATUS_NEW,
    LEAD_STATUS_NEEDS_INFO,
    LEAD_STATUS_QUALIFIED,
    LEAD_STATUS_NOTIFIED,
    LEAD_STATUS_CONTACTED,
    LEAD_STATUS_CLOSED,
    LEAD_STATUS_DISQUALIFIED,
}
BUSINESS_MANAGED_STATUSES = {
    LEAD_STATUS_CONTACTED,
    LEAD_STATUS_CLOSED,
    LEAD_STATUS_DISQUALIFIED,
}
TERMINAL_STATUSES = {LEAD_STATUS_CLOSED, LEAD_STATUS_DISQUALIFIED}
REQUIRED_QUALIFICATION_FIELDS = [
    "customer_name",
    "customer_phone",
    "job_type",
    "suburb",
    "urgency",
]
TRANSITIONS: dict[str, set[str]] = {
    LEAD_STATUS_NEW: {LEAD_STATUS_NEEDS_INFO, LEAD_STATUS_QUALIFIED, LEAD_STATUS_DISQUALIFIED},
    LEAD_STATUS_NEEDS_INFO: {LEAD_STATUS_QUALIFIED, LEAD_STATUS_DISQUALIFIED},
    LEAD_STATUS_QUALIFIED: {
        LEAD_STATUS_NOTIFIED,
        LEAD_STATUS_CONTACTED,
        LEAD_STATUS_DISQUALIFIED,
    },
    LEAD_STATUS_NOTIFIED: {LEAD_STATUS_CONTACTED, LEAD_STATUS_DISQUALIFIED},
    LEAD_STATUS_CONTACTED: {LEAD_STATUS_CLOSED, LEAD_STATUS_DISQUALIFIED},
    LEAD_STATUS_CLOSED: set(),
    LEAD_STATUS_DISQUALIFIED: set(),
}


@dataclass(frozen=True)
class LeadQualificationResult:
    """Result from deterministic lead qualification."""

    lead: Lead
    missing_fields: list[str]
    became_qualified: bool


class LeadWorkflowService:
    """Apply lifecycle state changes without LLM side effects."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def evaluate_qualification(self, lead: Lead) -> LeadQualificationResult:
        """Evaluate whether a lead is ready for business notification."""
        previous_status = lead.status
        missing_fields = self.missing_fields(lead)
        if lead.status in TERMINAL_STATUSES or lead.status in BUSINESS_MANAGED_STATUSES:
            return LeadQualificationResult(lead, missing_fields, became_qualified=False)

        if missing_fields:
            if lead.status == LEAD_STATUS_NEW:
                lead.status = LEAD_STATUS_NEEDS_INFO
            lead.qualification_reason = (
                "Missing required fields: " + ", ".join(missing_fields)
            )
            self.session.flush()
            return LeadQualificationResult(lead, missing_fields, became_qualified=False)

        if lead.status in {LEAD_STATUS_NEW, LEAD_STATUS_NEEDS_INFO}:
            lead.status = LEAD_STATUS_QUALIFIED
            lead.qualified_at = lead.qualified_at or utc_now()
            lead.qualification_reason = "Required lead fields captured."
        elif lead.status == LEAD_STATUS_QUALIFIED and lead.qualified_at is None:
            lead.qualified_at = utc_now()
            lead.qualification_reason = (
                lead.qualification_reason or "Required lead fields captured."
            )

        self.session.flush()
        return LeadQualificationResult(
            lead,
            missing_fields,
            became_qualified=(
                previous_status != LEAD_STATUS_QUALIFIED
                and lead.status == LEAD_STATUS_QUALIFIED
            ),
        )

    def update_business_status(self, lead: Lead, next_status: str) -> Lead:
        """Apply a business-managed lead status transition."""
        normalized_status = next_status.strip().lower()
        if normalized_status not in BUSINESS_MANAGED_STATUSES:
            raise ValueError("Status is not business-managed")
        allowed = TRANSITIONS.get(lead.status, set())
        if normalized_status not in allowed:
            raise ValueError(f"Cannot transition lead from {lead.status} to {normalized_status}")
        lead.status = normalized_status
        self.session.flush()
        return lead

    def mark_notified(self, lead: Lead) -> Lead:
        """Mark a qualified lead as notified after a successful delivery."""
        if lead.status == LEAD_STATUS_QUALIFIED:
            lead.status = LEAD_STATUS_NOTIFIED
        lead.notification_status = "sent"
        lead.last_notified_at = utc_now()
        self.session.flush()
        return lead

    def missing_fields(self, lead: Lead) -> list[str]:
        """Return missing fields required before notification."""
        return [
            field_name
            for field_name in REQUIRED_QUALIFICATION_FIELDS
            if not getattr(lead, field_name, None)
        ]
