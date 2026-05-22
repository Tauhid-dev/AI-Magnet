"""Chat API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LeadFields(BaseModel):
    """Deterministic lead fields that can be supplied by the widget."""

    customer_name: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None
    job_type: str | None = None
    suburb: str | None = None
    urgency: str | None = None
    notes: str | None = None


class ConversationStartRequest(BaseModel):
    """Start a widget conversation."""

    widget_key: str = Field(min_length=12)
    visitor_label: str | None = Field(default=None, max_length=255)
    origin: str | None = None


class ConversationStartResponse(BaseModel):
    """Conversation start response."""

    conversation_id: str
    status: str
    widget_key_prefix: str


class ConversationMessageRequest(BaseModel):
    """Post a visitor message to a conversation."""

    widget_key: str = Field(min_length=12)
    message: str = Field(min_length=1, max_length=4000)
    lead: LeadFields | None = None
    origin: str | None = None


class LeadCaptureState(BaseModel):
    """Lead capture progress returned to the widget."""

    lead_id: str | None = None
    captured_fields: list[str]
    missing_fields: list[str]
    next_prompt: str | None = None


class ConversationMessageResponse(BaseModel):
    """Assistant response and persisted message identifiers."""

    conversation_id: str
    visitor_message_id: str
    assistant_message_id: str
    assistant_message: str
    retrieved_chunk_count: int
    lead_capture: LeadCaptureState
