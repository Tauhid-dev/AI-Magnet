"""Super admin API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.audit.service import AuditService
from app.admin.auth import AdminPortalAuthService, AdminPortalSession
from app.admin.service import AdminService, TenantMetrics
from app.api.session_cookies import (
    clear_session_cookie,
    get_session_token_with_source,
    require_csrf_header_for_cookie_session,
    set_session_cookie,
)
from app.core.config import Settings, get_settings
from app.core.rate_limit import enforce_rate_limit
from app.db.session import get_db_session
from app.models.tenant import Business, BusinessUser, Tenant
from app.models.usage import AuditLog, UsageLog
from app.schemas.admin import (
    AdminAuditLogResponse,
    AdminAnalyticsBreakdownResponse,
    AdminBusinessResponse,
    AdminBusinessUserResponse,
    AdminHealthResponse,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminSessionResponse,
    AdminSupportContextResponse,
    AdminSupportConversationResponse,
    AdminSupportLeadResponse,
    AdminTenantCreateRequest,
    AdminTenantDetailResponse,
    AdminTenantMetricsResponse,
    AdminTenantStatusUpdateRequest,
    AdminTenantSummaryResponse,
    AdminTenantUsageSummaryResponse,
    AdminUsageEventResponse,
    AdminUsageOverviewResponse,
)


router = APIRouter(prefix="/admin", tags=["admin"])

ALLOWED_TENANT_STATUSES = {"active", "suspended", "inactive"}


def get_current_admin_session(
    request: Request,
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AdminPortalSession:
    """Resolve a cookie or bearer token to a super admin session."""
    resolved_token = get_session_token_with_source(
        request,
        authorization,
        cookie_name=settings.admin_portal_cookie_name,
    )
    if resolved_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing super admin session",
        )
    require_csrf_header_for_cookie_session(request, resolved_token)
    admin_session = AdminPortalAuthService(session, settings).verify_token(
        resolved_token.token
    )
    if admin_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid super admin session",
        )
    return admin_session


def admin_session_response(admin_session: AdminPortalSession) -> AdminSessionResponse:
    """Map session context to a safe response."""
    return AdminSessionResponse(
        admin_id=admin_session.admin_id,
        email=admin_session.email,
        full_name=admin_session.full_name,
        role=admin_session.role,
    )


@router.post("/auth/login", response_model=AdminLoginResponse)
def login(
    request: Request,
    payload: AdminLoginRequest,
    response: Response,
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AdminLoginResponse:
    """Create a signed session for an active super admin."""
    enforce_rate_limit(
        request,
        settings,
        scope="admin_login",
        identifiers=[payload.email],
        limit=settings.rate_limit_login_per_minute,
    )
    result = AdminPortalAuthService(session, settings).login(
        email=payload.email,
        password=payload.password,
        mfa_code=payload.mfa_code,
    )
    if result is None:
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid super admin login",
        )
    token, admin_session = result
    session.commit()
    set_session_cookie(
        response,
        name=settings.admin_portal_cookie_name,
        token=token,
        max_age_seconds=settings.admin_portal_session_ttl_minutes * 60,
        settings=settings,
    )
    return AdminLoginResponse(
        access_token=token,
        session=admin_session_response(admin_session),
    )


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    admin_session: AdminPortalSession = Depends(get_current_admin_session),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> Response:
    """Revoke current admin sessions and clear the browser cookie."""
    AdminPortalAuthService(session, settings).revoke_sessions(admin_session.admin_id)
    session.commit()
    clear_session_cookie(response, name=settings.admin_portal_cookie_name, settings=settings)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/session", response_model=AdminSessionResponse)
def get_session(
    admin_session: AdminPortalSession = Depends(get_current_admin_session),
) -> AdminSessionResponse:
    """Return the current super admin session."""
    return admin_session_response(admin_session)


@router.get("/tenants", response_model=list[AdminTenantSummaryResponse])
def list_tenants(
    _admin_session: AdminPortalSession = Depends(get_current_admin_session),
    session: Session = Depends(get_db_session),
) -> list[AdminTenantSummaryResponse]:
    """List tenants with compact metrics."""
    service = AdminService(session)
    return [tenant_summary_response(service, tenant) for tenant in service.list_tenants()]


@router.post("/tenants", response_model=AdminTenantDetailResponse)
def create_tenant(
    request: Request,
    payload: AdminTenantCreateRequest,
    admin_session: AdminPortalSession = Depends(get_current_admin_session),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AdminTenantDetailResponse:
    """Create a tenant and initial business account."""
    enforce_rate_limit(
        request,
        settings,
        scope="admin_tenant_create",
        identifiers=[admin_session.admin_id],
        limit=settings.rate_limit_admin_write_per_minute,
    )
    if payload.status not in ALLOWED_TENANT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported tenant status",
        )
    if payload.owner_email and not payload.owner_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner password is required when owner email is provided",
        )
    service = AdminService(session)
    try:
        tenant = service.create_tenant(
            name=payload.name,
            slug=payload.slug,
            status=payload.status,
            business_name=payload.business_name,
            business_email=payload.business_email,
            owner_email=payload.owner_email,
            owner_password=payload.owner_password,
        )
        AuditService(session).record_admin_action(
            tenant_id=tenant.id,
            actor_id=admin_session.admin_id,
            action="tenant_created",
            target_type="tenant",
            target_id=tenant.id,
            attributes={"status": tenant.status, "slug": tenant.slug},
        )
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant or business user already exists",
        ) from exc
    return tenant_detail_response(service, tenant)


@router.get("/tenants/{tenant_id}", response_model=AdminTenantDetailResponse)
def get_tenant(
    tenant_id: str,
    admin_session: AdminPortalSession = Depends(get_current_admin_session),
    session: Session = Depends(get_db_session),
) -> AdminTenantDetailResponse:
    """Return tenant detail for super admins."""
    service = AdminService(session)
    tenant = service.get_tenant(tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    AuditService(session).record_admin_action(
        tenant_id=tenant.id,
        actor_id=admin_session.admin_id,
        action="tenant_detail_viewed",
        target_type="tenant",
        target_id=tenant.id,
        attributes={"slug": tenant.slug},
    )
    session.commit()
    return tenant_detail_response(service, tenant)


@router.patch("/tenants/{tenant_id}/status", response_model=AdminTenantDetailResponse)
def update_tenant_status(
    request: Request,
    tenant_id: str,
    payload: AdminTenantStatusUpdateRequest,
    admin_session: AdminPortalSession = Depends(get_current_admin_session),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AdminTenantDetailResponse:
    """Update a tenant lifecycle status."""
    enforce_rate_limit(
        request,
        settings,
        scope="admin_tenant_status_write",
        identifiers=[admin_session.admin_id, tenant_id],
        limit=settings.rate_limit_admin_write_per_minute,
    )
    if payload.status not in ALLOWED_TENANT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported tenant status",
        )
    service = AdminService(session)
    tenant = service.update_tenant_status(tenant_id, payload.status)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    AuditService(session).record_admin_action(
        tenant_id=tenant.id,
        actor_id=admin_session.admin_id,
        action="tenant_status_updated",
        target_type="tenant",
        target_id=tenant.id,
        attributes={"status": tenant.status},
    )
    session.commit()
    return tenant_detail_response(service, tenant)


@router.get(
    "/tenants/{tenant_id}/support-context",
    response_model=AdminSupportContextResponse,
)
def get_support_context(
    tenant_id: str,
    admin_session: AdminPortalSession = Depends(get_current_admin_session),
    session: Session = Depends(get_db_session),
) -> AdminSupportContextResponse:
    """Return limited tenant support context and record the access."""
    service = AdminService(session)
    tenant = service.get_tenant(tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    AuditService(session).record_admin_action(
        tenant_id=tenant.id,
        actor_id=admin_session.admin_id,
        action="tenant_support_context_viewed",
        target_type="tenant",
        target_id=tenant.id,
        attributes={"slug": tenant.slug},
    )
    session.commit()
    return AdminSupportContextResponse(
        tenant=tenant_summary_response(service, tenant),
        recent_leads=[
            AdminSupportLeadResponse(
                id=lead.id,
                status=lead.status,
                job_type=lead.job_type,
                suburb=lead.suburb,
                urgency=lead.urgency,
                has_contact=bool(lead.customer_email or lead.customer_phone),
                created_at=lead.created_at,
            )
            for lead in service.recent_leads(tenant.id)
        ],
        recent_conversations=[
            AdminSupportConversationResponse(
                id=conversation.id,
                status=conversation.status,
                source=conversation.source,
                created_at=conversation.created_at,
                message_count=service.message_count(conversation.id, tenant.id),
            )
            for conversation in service.recent_conversations(tenant.id)
        ],
        recent_usage=[usage_event_response(event) for event in service.recent_usage(tenant.id)],
    )


@router.get("/usage", response_model=AdminUsageOverviewResponse)
def get_usage_overview(
    _admin_session: AdminPortalSession = Depends(get_current_admin_session),
    session: Session = Depends(get_db_session),
) -> AdminUsageOverviewResponse:
    """Return platform-wide usage totals."""
    overview = AdminService(session).usage_overview()
    return AdminUsageOverviewResponse(
        tenants_total=overview.tenants_total,
        active_tenants=overview.active_tenants,
        documents_total=overview.documents_total,
        documents_ingested=overview.documents_ingested,
        leads_total=overview.leads_total,
        leads_qualified=overview.leads_qualified,
        conversations_total=overview.conversations_total,
        messages_total=overview.messages_total,
        usage_events_total=overview.usage_events_total,
        ai_responses_total=overview.ai_responses_total,
        lead_notifications_sent=overview.lead_notifications_sent,
        admin_audit_events_total=overview.admin_audit_events_total,
        usage_event_counts=[admin_breakdown_response(item) for item in overview.usage_event_counts],
        lead_status_counts=[admin_breakdown_response(item) for item in overview.lead_status_counts],
        document_status_counts=[
            admin_breakdown_response(item) for item in overview.document_status_counts
        ],
        tenant_usage=[
            AdminTenantUsageSummaryResponse(
                tenant_id=item.tenant_id,
                tenant_name=item.tenant_name,
                tenant_slug=item.tenant_slug,
                tenant_status=item.tenant_status,
                documents_total=item.documents_total,
                leads_total=item.leads_total,
                conversations_total=item.conversations_total,
                messages_total=item.messages_total,
                usage_events_total=item.usage_events_total,
            )
            for item in overview.tenant_usage
        ],
    )


@router.get("/health", response_model=AdminHealthResponse)
def get_admin_health(
    _admin_session: AdminPortalSession = Depends(get_current_admin_session),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> AdminHealthResponse:
    """Return backend health details for super admins."""
    database = "ok"
    status_value = "ok"
    try:
        session.execute(select(func.count(Tenant.id))).scalar()
    except Exception:
        database = "error"
        status_value = "degraded"
    return AdminHealthResponse(
        status=status_value,
        database=database,
        app_version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/audit-logs", response_model=list[AdminAuditLogResponse])
def list_audit_logs(
    _admin_session: AdminPortalSession = Depends(get_current_admin_session),
    session: Session = Depends(get_db_session),
) -> list[AdminAuditLogResponse]:
    """List recent tenant-scoped audit events."""
    return [audit_log_response(event) for event in AdminService(session).recent_audit_logs()]


def tenant_summary_response(
    service: AdminService,
    tenant: Tenant,
) -> AdminTenantSummaryResponse:
    """Map tenant and metrics to a summary response."""
    return AdminTenantSummaryResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        status=tenant.status,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
        metrics=metrics_response(service.tenant_metrics(tenant.id)),
    )


def tenant_detail_response(
    service: AdminService,
    tenant: Tenant,
) -> AdminTenantDetailResponse:
    """Map tenant detail and related business account data."""
    base = tenant_summary_response(service, tenant)
    base_payload = base.model_dump() if hasattr(base, "model_dump") else base.dict()
    return AdminTenantDetailResponse(
        **base_payload,
        businesses=[business_response(business) for business in service.list_businesses(tenant.id)],
        users=[business_user_response(user) for user in service.list_business_users(tenant.id)],
    )


def metrics_response(metrics: TenantMetrics) -> AdminTenantMetricsResponse:
    """Map tenant metrics to API response."""
    return AdminTenantMetricsResponse(
        businesses_total=metrics.businesses_total,
        users_total=metrics.users_total,
        documents_total=metrics.documents_total,
        leads_total=metrics.leads_total,
        conversations_total=metrics.conversations_total,
        messages_total=metrics.messages_total,
        usage_events_total=metrics.usage_events_total,
    )


def business_response(business: Business) -> AdminBusinessResponse:
    """Map business profile to admin response."""
    return AdminBusinessResponse(
        id=business.id,
        name=business.name,
        email=business.email,
        phone=business.phone,
        website_url=business.website_url,
        created_at=business.created_at,
    )


def business_user_response(user: BusinessUser) -> AdminBusinessUserResponse:
    """Map business user to admin response."""
    return AdminBusinessUserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        status=user.status,
        created_at=user.created_at,
    )


def usage_event_response(event: UsageLog) -> AdminUsageEventResponse:
    """Map usage log to admin response."""
    return AdminUsageEventResponse(
        event_type=event.event_type,
        event_source=event.event_source,
        attributes=event.attributes or {},
        created_at=event.created_at,
    )


def admin_breakdown_response(item) -> AdminAnalyticsBreakdownResponse:
    """Map analytics breakdown to admin response."""
    return AdminAnalyticsBreakdownResponse(label=item.label, count=item.count)


def audit_log_response(event: AuditLog) -> AdminAuditLogResponse:
    """Map audit log to admin response."""
    return AdminAuditLogResponse(
        id=event.id,
        tenant_id=event.tenant_id,
        actor_id=event.actor_id,
        action=event.action,
        target_type=event.target_type,
        target_id=event.target_id,
        attributes=event.attributes or {},
        created_at=event.created_at,
    )
