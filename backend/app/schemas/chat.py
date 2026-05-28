"""Chat API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LeadFields(BaseModel):
    """Deterministic lead fields that can be supplied by the widget."""

    customer_name: str | None = Field(default=None, max_length=255)
    customer_email: str | None = Field(default=None, max_length=255)
    customer_phone: str | None = Field(default=None, max_length=80)
    job_type: str | None = Field(default=None, max_length=120)
    suburb: str | None = Field(default=None, max_length=120)
    urgency: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=2000)


class ConversationStartRequest(BaseModel):
    """Start a widget conversation."""

    widget_key: str = Field(min_length=12, max_length=256)
    visitor_label: str | None = Field(default=None, max_length=255)
    origin: str | None = Field(default=None, max_length=500)


class ConversationStartResponse(BaseModel):
    """Conversation start response."""

    conversation_id: str
    status: str
    widget_key_prefix: str


class ConversationMessageRequest(BaseModel):
    """Post a visitor message to a conversation."""

    widget_key: str = Field(min_length=12, max_length=256)
    message: str = Field(min_length=1, max_length=4000)
    lead: LeadFields | None = None
    origin: str | None = Field(default=None, max_length=500)


class LeadCaptureState(BaseModel):
    """Lead capture progress returned to the widget."""

    lead_id: str | None = None
    captured_fields: list[str]
    missing_fields: list[str]
    next_prompt: str | None = None


class CitationSource(BaseModel):
    """Source metadata for a grounded chat answer citation."""

    citation_id: str
    document_id: str
    chunk_id: str
    chunk_index: int
    score: float
    filename: str
    source_type: str
    source_title: str | None = None
    source_url: str | None = None


class ConversationMessageResponse(BaseModel):
    """Assistant response and persisted message identifiers."""

    conversation_id: str
    visitor_message_id: str
    assistant_message_id: str
    assistant_message: str
    retrieved_chunk_count: int
    citations: list[CitationSource] = Field(default_factory=list)
    answer_status: str = "answered"
    retrieval_latency_ms: int = 0
    retrieval_top_score: float | None = None
    rag_safety_flags: list[str] = Field(default_factory=list)
    lead_capture: LeadCaptureState
