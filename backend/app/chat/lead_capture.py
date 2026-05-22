"""Deterministic lead capture helpers for chat conversations."""

from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.schemas.chat import LeadFields


EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?:\+?61|0)?(?:[\s-]?\d){8,10}")
JOB_KEYWORDS = {
    "blocked drain": "blocked drain",
    "hot water": "hot water",
    "leak": "leak repair",
    "toilet": "toilet repair",
    "tap": "tap repair",
    "roof": "roof repair",
    "power": "electrical",
}
URGENCY_KEYWORDS = {
    "emergency": "emergency",
    "urgent": "urgent",
    "today": "today",
    "tomorrow": "soon",
    "after hours": "after hours",
}
REQUIRED_FIELDS = [
    "customer_name",
    "customer_phone",
    "job_type",
    "suburb",
    "urgency",
]
PROMPTS = {
    "customer_name": "Could I grab your name for the booking request?",
    "customer_phone": "What is the best phone number for the tradie to call back on?",
    "job_type": "What type of job do you need help with?",
    "suburb": "Which suburb is the job in?",
    "urgency": "How urgent is this job?",
}


@dataclass(frozen=True)
class LeadCaptureResult:
    """Lead capture state after processing a visitor message."""

    lead: Lead | None
    captured_fields: list[str]
    missing_fields: list[str]
    next_prompt: str | None


class LeadCaptureService:
    """Extract and persist predictable lead fields without relying on an LLM."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def capture(
        self,
        tenant_id: str,
        conversation_id: str,
        message: str,
        provided_fields: LeadFields | None = None,
    ) -> LeadCaptureResult:
        """Create or update a tenant-scoped lead for a conversation."""
        fields = self._extract_fields(message)
        if provided_fields is not None:
            provided = (
                provided_fields.model_dump()
                if hasattr(provided_fields, "model_dump")
                else provided_fields.dict()
            )
            fields.update(
                {
                    key: value
                    for key, value in provided.items()
                    if value
                }
            )

        lead = self._get_or_create_lead(tenant_id, conversation_id)
        for field_name, value in fields.items():
            if value and hasattr(lead, field_name):
                setattr(lead, field_name, value)

        if fields and message not in (lead.notes or ""):
            lead.notes = self._append_note(lead.notes, message)

        captured = [
            field_name
            for field_name in REQUIRED_FIELDS
            if getattr(lead, field_name, None)
        ]
        missing = [field_name for field_name in REQUIRED_FIELDS if field_name not in captured]
        next_prompt = PROMPTS.get(missing[0]) if missing else None
        self.session.flush()
        return LeadCaptureResult(
            lead=lead,
            captured_fields=captured,
            missing_fields=missing,
            next_prompt=next_prompt,
        )

    def _get_or_create_lead(self, tenant_id: str, conversation_id: str) -> Lead:
        statement = select(Lead).where(
            Lead.tenant_id == tenant_id,
            Lead.conversation_id == conversation_id,
        )
        lead = self.session.scalars(statement).first()
        if lead is not None:
            return lead
        lead = Lead(tenant_id=tenant_id, conversation_id=conversation_id, status="new")
        self.session.add(lead)
        self.session.flush()
        return lead

    def _extract_fields(self, message: str) -> dict[str, str]:
        lowered = message.lower()
        fields: dict[str, str] = {}

        email_match = EMAIL_RE.search(message)
        if email_match:
            fields["customer_email"] = email_match.group(0)

        phone_match = PHONE_RE.search(message)
        if phone_match:
            fields["customer_phone"] = phone_match.group(0).strip()

        for keyword, job_type in JOB_KEYWORDS.items():
            if keyword in lowered:
                fields["job_type"] = job_type
                break

        for keyword, urgency in URGENCY_KEYWORDS.items():
            if keyword in lowered:
                fields["urgency"] = urgency
                break

        suburb = self._extract_labeled_value(message, ("suburb", "in"))
        if suburb:
            fields["suburb"] = suburb

        name = self._extract_labeled_value(message, ("name is", "i am", "i'm"))
        if name:
            fields["customer_name"] = name

        return fields

    def _extract_labeled_value(self, message: str, labels: tuple[str, ...]) -> str | None:
        lowered = message.lower()
        for label in labels:
            marker = f"{label} "
            index = lowered.find(marker)
            if index == -1:
                continue
            value = message[index + len(marker) :].strip(" .,!?:;")
            if not value:
                continue
            return value.split(",")[0].strip()[:160]
        return None

    def _append_note(self, existing: str | None, message: str) -> str:
        if not existing:
            return message[:1000]
        return f"{existing}\n{message}"[:2000]
