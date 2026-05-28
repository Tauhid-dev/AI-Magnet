"""Business portal API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BusinessPortalLoginRequest(BaseModel):
    """Business portal login request."""

    tenant_slug: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=256)


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
    source_type: str = "manual_upload"
    source_url: str | None = None
    source_title: str | None = None
    website_source_id: str | None = None
    file_size_bytes: int | None = None
    file_sha256: str | None = None
    malware_scan_status: str = "not_scanned"
    extraction_status: str = "pending"
    ocr_status: str = "not_required"
    job_id: str | None = None
    created_at: datetime
    updated_at: datetime


class PortalDocumentCreateRequest(BaseModel):
    """Simple text document upload request for the MVP portal."""

    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    content_type: str = "text/plain"


class PortalWebsiteSourceCreateRequest(BaseModel):
    """Website or sitemap ingestion request."""

    source_type: str = Field(min_length=1, max_length=40)
    url: str = Field(min_length=8, max_length=2000)
    max_pages: int | None = Field(default=None, ge=1, le=100)
    max_depth: int | None = Field(default=None, ge=0, le=5)


class PortalWebsiteSourceResponse(BaseModel):
    """Tenant-owned website/sitemap source status."""

    id: str
    source_type: str
    root_url: str
    normalized_domain: str
    status: str
    last_job_id: str | None
    last_error: str | None
    max_pages: int
    max_depth: int
    last_crawled_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PortalWebsiteCrawlPageResponse(BaseModel):
    """Crawl history row for a tenant website/sitemap source."""

    id: str
    source_id: str
    url: str
    canonical_url: str
    title: str | None
    status: str
    http_status: int | None
    error_message: str | None
    document_id: str | None
    crawled_at: datetime | None
    created_at: datetime
    updated_at: datetime


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
    allowed_origins: list[str]


class PortalWidgetKeyCreateRequest(BaseModel):
    """Widget key creation request with explicit allowed browser origins."""

    allowed_origins: list[str] = Field(default_factory=list)


class PortalWidgetOriginsUpdateRequest(BaseModel):
    """Widget allowed origin update request."""

    allowed_origins: list[str] = Field(default_factory=list)


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


class PortalJobResponse(BaseModel):
    """Tenant-visible background job status without raw payload data."""

    id: str
    job_type: str
    status: str
    attempts: int
    max_attempts: int
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    failed_at: datetime | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime


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
