"""Notification templates for lead workflows."""

from __future__ import annotations

from app.models.lead import Lead


def lead_notification_subject(lead: Lead) -> str:
    """Return a concise lead notification subject."""
    job_type = lead.job_type or "New enquiry"
    suburb = lead.suburb or "unknown suburb"
    return f"New qualified lead: {job_type} in {suburb}"


def lead_notification_body(lead: Lead) -> str:
    """Return a plain-text lead notification body."""
    lines = [
        "A new qualified lead was captured by the AI receptionist.",
        "",
        f"Customer: {lead.customer_name or '-'}",
        f"Phone: {lead.customer_phone or '-'}",
        f"Email: {lead.customer_email or '-'}",
        f"Job type: {lead.job_type or '-'}",
        f"Suburb: {lead.suburb or '-'}",
        f"Urgency: {lead.urgency or '-'}",
    ]
    if lead.notes:
        lines.extend(["", "Conversation notes:", lead.notes[:1200]])
    return "\n".join(lines)
