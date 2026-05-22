"""Business portal API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BusinessPortalLoginRequest(BaseModel):
    """Business portal login request."""

    tenant_slug: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=255)


class BusinessPortalSessionResponse(BaseModel):
    """Safe business portal session response."""

    tenant_id: str
    tenant_name: str
    tenant_slug: str
    user_id: str
    email: str
    role: str


class BusinessPortalLoginResponse(BaseModel):
    """Business portal login response."""

    access_token: str
    token_type: str = "bearer"
    session: BusinessPortalSessionResponse


class PortalDocumentResponse(BaseModel):
    """Knowledge document row for the business portal."""

    id: str
    filename: str
    content_type: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class PortalDocumentCreateRequest(BaseModel):
    """Simple text document upload request for the MVP portal."""

    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    content_type: str = "text/plain"


class PortalLeadResponse(BaseModel):
    """Lead row for the business portal."""

    id: str
    conversation_id: str | None
    customer_name: str | None
    customer_email: str | None
    customer_phone: str | None
    job_type: str | None
    suburb: str | None
    urgency: str | None
    status: str
    qualified_at: datetime | None
    qualification_reason: str | None
    notification_status: str
    last_notified_at: datetime | None
    notes: str | None
    created_at: datetime


class PortalLeadStatusUpdateRequest(BaseModel):
    """Lead status update request from the business portal."""

    status: str = Field(min_length=1, max_length=60)


class PortalMessageResponse(BaseModel):
    """Conversation message row."""

    id: str
    sender_type: str
    content: str
    created_at: datetime


class PortalConversationResponse(BaseModel):
    """Conversation row for the business portal."""

    id: str
    visitor_label: str | None
    status: str
    source: str
    created_at: datetime
    message_count: int = 0


class PortalConversationDetailResponse(PortalConversationResponse):
    """Conversation detail with messages."""

    messages: list[PortalMessageResponse]


class PortalWidgetResponse(BaseModel):
    """Business portal widget setup response."""

    id: str | None
    status: str
    key_prefix: str | None
    widget_key: str | None = None
    embed_code: str | None
    allowed_origins: str | None


class PortalAnalyticsBreakdownResponse(BaseModel):
    """Analytics label/count pair."""

    label: str
    count: int


class PortalUsageEventResponse(BaseModel):
    """Recent tenant usage event."""

    event_type: str
    event_source: str | None
    attributes: dict[str, Any]
    created_at: datetime


class PortalAnalyticsResponse(BaseModel):
    """Business portal analytics response."""

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
    lead_status_counts: list[PortalAnalyticsBreakdownResponse]
    document_status_counts: list[PortalAnalyticsBreakdownResponse]
    usage_event_counts: list[PortalAnalyticsBreakdownResponse]
    recent_usage: list[PortalUsageEventResponse]
