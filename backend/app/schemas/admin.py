"""Super admin API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    """Super admin login request."""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=256)
    mfa_code: str | None = Field(default=None, min_length=6, max_length=20)


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
    offboarded_at: datetime | None = None
    deletion_requested_at: datetime | None = None
    data_retention_until: datetime | None = None
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
    owner_password: str | None = Field(default=None, min_length=8, max_length=256)


class AdminTenantStatusUpdateRequest(BaseModel):
    """Update tenant lifecycle status."""

    status: str = Field(min_length=1, max_length=40)


class AdminTenantOffboardRequest(BaseModel):
    """Mark a tenant for offboarding and retention tracking."""

    retention_days: int | None = Field(default=None, ge=1, le=3650)


class AdminTenantDeleteRequest(BaseModel):
    """Explicit confirmation for destructive tenant data deletion."""

    confirm_slug: str = Field(min_length=1, max_length=120)
    confirm_delete: bool = False


class AdminTenantDeleteResponse(BaseModel):
    """Response after tenant data deletion."""

    tenant_id: str
    tenant_slug: str
    status: str
    global_audit_id: str


class AdminTenantPrivacyExportResponse(BaseModel):
    """Beta-scope tenant data export response."""

    tenant_id: str
    generated_at: datetime
    data: dict[str, Any]


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
    estimated_tokens_total: int
    estimated_cost_cents_total: float
    pages_crawled_total: int
    storage_mb_total: float
    rate_limit_events_total: int
    quota_warning_tenants: int
    quota_blocked_tenants: int
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
    estimated_tokens: int
    estimated_cost_cents: float
    quota_warnings: list[str]
    quota_blockers: list[str]


class AdminHealthResponse(BaseModel):
    """Super admin system health response."""

    status: str
    database: str
    queued_jobs: int = 0
    running_jobs: int = 0
    failed_jobs: int = 0
    active_workers: int = 0
    app_version: str
    environment: str


class AdminJobResponse(BaseModel):
    """Super-admin background job status without raw payload data."""

    id: str
    tenant_id: str | None
    queue_name: str
    job_type: str
    status: str
    attempts: int
    max_attempts: int
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    failed_at: datetime | None
    locked_by: str | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime


class AdminWorkerHeartbeatResponse(BaseModel):
    """Worker heartbeat visible to super admins."""

    worker_id: str
    queue_name: str
    status: str
    hostname: str | None
    pid: int | None
    current_job_id: str | None
    last_seen_at: datetime
    stopping_at: datetime | None


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
    """Tenant-scoped or global audit log row."""

    id: str
    scope: str
    tenant_id: str | None
    actor_id: str | None
    action: str
    target_type: str | None
    target_id: str | None
    attributes: dict[str, Any]
    created_at: datetime
