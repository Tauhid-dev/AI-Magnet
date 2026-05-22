"""Super admin API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    """Super admin login request."""

    email: str = Field(min_length=3, max_length=255)


class AdminSessionResponse(BaseModel):
    """Safe super admin session response."""

    admin_id: str
    email: str
    full_name: str | None
    role: str


class AdminLoginResponse(BaseModel):
    """Super admin login response."""

    access_token: str
    token_type: str = "bearer"
    session: AdminSessionResponse


class AdminTenantMetricsResponse(BaseModel):
    """Tenant metrics for admin views."""

    businesses_total: int
    users_total: int
    documents_total: int
    leads_total: int
    conversations_total: int
    messages_total: int
    usage_events_total: int


class AdminTenantSummaryResponse(BaseModel):
    """Tenant row for the super admin portal."""

    id: str
    name: str
    slug: str
    status: str
    created_at: datetime
    updated_at: datetime
    metrics: AdminTenantMetricsResponse


class AdminBusinessResponse(BaseModel):
    """Business profile visible to super admins."""

    id: str
    name: str
    email: str | None
    phone: str | None
    website_url: str | None
    created_at: datetime


class AdminBusinessUserResponse(BaseModel):
    """Business user row visible to super admins."""

    id: str
    email: str
    full_name: str | None
    role: str
    status: str
    created_at: datetime


class AdminTenantDetailResponse(AdminTenantSummaryResponse):
    """Tenant detail with business account context."""

    businesses: list[AdminBusinessResponse]
    users: list[AdminBusinessUserResponse]


class AdminTenantCreateRequest(BaseModel):
    """Create a tenant and initial business account."""

    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=120)
    status: str = Field(default="active", max_length=40)
    business_name: str | None = Field(default=None, max_length=255)
    business_email: str | None = Field(default=None, max_length=255)
    owner_email: str | None = Field(default=None, max_length=255)


class AdminTenantStatusUpdateRequest(BaseModel):
    """Update tenant lifecycle status."""

    status: str = Field(min_length=1, max_length=40)


class AdminUsageOverviewResponse(BaseModel):
    """Platform-wide usage overview."""

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
    usage_event_counts: list["AdminAnalyticsBreakdownResponse"]
    lead_status_counts: list["AdminAnalyticsBreakdownResponse"]
    document_status_counts: list["AdminAnalyticsBreakdownResponse"]
    tenant_usage: list["AdminTenantUsageSummaryResponse"]


class AdminAnalyticsBreakdownResponse(BaseModel):
    """Analytics label/count pair for admin views."""

    label: str
    count: int


class AdminTenantUsageSummaryResponse(BaseModel):
    """Tenant usage row for admin analytics."""

    tenant_id: str
    tenant_name: str
    tenant_slug: str
    tenant_status: str
    documents_total: int
    leads_total: int
    conversations_total: int
    messages_total: int
    usage_events_total: int


class AdminHealthResponse(BaseModel):
    """Super admin system health response."""

    status: str
    database: str
    app_version: str
    environment: str


class AdminSupportLeadResponse(BaseModel):
    """Limited lead context for support views."""

    id: str
    status: str
    job_type: str | None
    suburb: str | None
    urgency: str | None
    has_contact: bool
    created_at: datetime


class AdminSupportConversationResponse(BaseModel):
    """Limited conversation context for support views."""

    id: str
    status: str
    source: str
    created_at: datetime
    message_count: int


class AdminUsageEventResponse(BaseModel):
    """Usage event visible in admin support context."""

    event_type: str
    event_source: str | None
    attributes: dict[str, Any]
    created_at: datetime


class AdminSupportContextResponse(BaseModel):
    """Tenant support context with limited PII exposure."""

    tenant: AdminTenantSummaryResponse
    recent_leads: list[AdminSupportLeadResponse]
    recent_conversations: list[AdminSupportConversationResponse]
    recent_usage: list[AdminUsageEventResponse]


class AdminAuditLogResponse(BaseModel):
    """Tenant-scoped audit log row."""

    id: str
    tenant_id: str
    actor_id: str | None
    action: str
    target_type: str | None
    target_id: str | None
    attributes: dict[str, Any]
    created_at: datetime
