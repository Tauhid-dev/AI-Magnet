"""Tenant-scoped business portal API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.business.auth import BusinessPortalAuthService, BusinessPortalSession
from app.business.service import BusinessPortalService
from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.providers.ai.factory import get_embedding_provider
from app.rag.ingestion import RagIngestionService
from app.schemas.business_portal import (
    BusinessPortalLoginRequest,
    BusinessPortalLoginResponse,
    BusinessPortalSessionResponse,
    PortalAnalyticsResponse,
    PortalConversationDetailResponse,
    PortalConversationResponse,
    PortalDocumentCreateRequest,
    PortalDocumentResponse,
    PortalLeadResponse,
    PortalLeadStatusUpdateRequest,
    PortalMessageResponse,
    PortalWidgetResponse,
)
from app.widget.service import WidgetService


router = APIRouter(prefix="/business-portal", tags=["business-portal"])


def get_current_business_session(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> BusinessPortalSession:
    """Resolve a bearer token to a tenant-scoped business session."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing business portal session",
        )
    token = authorization.split(" ", 1)[1]
    portal_session = BusinessPortalAuthService(session, settings).verify_token(token)
    if portal_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid business portal session",
        )
    return portal_session


def session_response(session: BusinessPortalSession) -> BusinessPortalSessionResponse:
    """Map session context to a response model."""
    return BusinessPortalSessionResponse(
        tenant_id=session.tenant_id,
        tenant_name=session.tenant_name,
        tenant_slug=session.tenant_slug,
        user_id=session.user_id,
        email=session.email,
        role=session.role,
    )


@router.post("/auth/login", response_model=BusinessPortalLoginResponse)
def login(
    payload: BusinessPortalLoginRequest,
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> BusinessPortalLoginResponse:
    """Create a signed business portal session for an active user."""
    result = BusinessPortalAuthService(session, settings).login(
        tenant_slug=payload.tenant_slug,
        email=payload.email,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid business portal login",
        )
    token, portal_session = result
    return BusinessPortalLoginResponse(
        access_token=token,
        session=session_response(portal_session),
    )


@router.get("/session", response_model=BusinessPortalSessionResponse)
def get_session(
    portal_session: BusinessPortalSession = Depends(get_current_business_session),
) -> BusinessPortalSessionResponse:
    """Return the current business portal session."""
    return session_response(portal_session)


@router.get("/documents", response_model=list[PortalDocumentResponse])
def list_documents(
    portal_session: BusinessPortalSession = Depends(get_current_business_session),
    session: Session = Depends(get_db_session),
) -> list[PortalDocumentResponse]:
    """List current tenant knowledge documents."""
    documents = BusinessPortalService(session, portal_session.tenant_id).list_documents()
    return [
        PortalDocumentResponse(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            status=document.status,
            error_message=document.error_message,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
        for document in documents
    ]


@router.post("/documents", response_model=PortalDocumentResponse)
def create_document(
    payload: PortalDocumentCreateRequest,
    portal_session: BusinessPortalSession = Depends(get_current_business_session),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> PortalDocumentResponse:
    """Ingest a text document for the current tenant."""
    embedding_provider = get_embedding_provider(settings)
    document = RagIngestionService(
        session=session,
        embedding_provider=embedding_provider,
        settings=settings,
    ).ingest_bytes(
        tenant_id=portal_session.tenant_id,
        filename=payload.filename,
        content=payload.content.encode("utf-8"),
        content_type=payload.content_type,
    )
    session.commit()
    return PortalDocumentResponse(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        status=document.status,
        error_message=document.error_message,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


@router.get("/leads", response_model=list[PortalLeadResponse])
def list_leads(
    portal_session: BusinessPortalSession = Depends(get_current_business_session),
    session: Session = Depends(get_db_session),
) -> list[PortalLeadResponse]:
    """List current tenant leads."""
    leads = BusinessPortalService(session, portal_session.tenant_id).list_leads()
    return [lead_response(lead) for lead in leads]


@router.get("/leads/{lead_id}", response_model=PortalLeadResponse)
def get_lead(
    lead_id: str,
    portal_session: BusinessPortalSession = Depends(get_current_business_session),
    session: Session = Depends(get_db_session),
) -> PortalLeadResponse:
    """Return a current tenant lead by id."""
    lead = BusinessPortalService(session, portal_session.tenant_id).get_lead(lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead_response(lead)


@router.patch("/leads/{lead_id}/status", response_model=PortalLeadResponse)
def update_lead_status(
    lead_id: str,
    payload: PortalLeadStatusUpdateRequest,
    portal_session: BusinessPortalSession = Depends(get_current_business_session),
    session: Session = Depends(get_db_session),
) -> PortalLeadResponse:
    """Update a current tenant lead lifecycle status."""
    service = BusinessPortalService(session, portal_session.tenant_id)
    try:
        lead = service.update_lead_status(lead_id, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    session.commit()
    return lead_response(lead)


@router.get("/conversations", response_model=list[PortalConversationResponse])
def list_conversations(
    portal_session: BusinessPortalSession = Depends(get_current_business_session),
    session: Session = Depends(get_db_session),
) -> list[PortalConversationResponse]:
    """List current tenant conversations."""
    service = BusinessPortalService(session, portal_session.tenant_id)
    return [
        conversation_response(conversation, len(conversation.messages))
        for conversation in service.list_conversations()
    ]


@router.get(
    "/conversations/{conversation_id}",
    response_model=PortalConversationDetailResponse,
)
def get_conversation(
    conversation_id: str,
    portal_session: BusinessPortalSession = Depends(get_current_business_session),
    session: Session = Depends(get_db_session),
) -> PortalConversationDetailResponse:
    """Return a current tenant conversation with messages."""
    service = BusinessPortalService(session, portal_session.tenant_id)
    conversation = service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    messages = [
        PortalMessageResponse(
            id=message.id,
            sender_type=message.sender_type,
            content=message.content,
            created_at=message.created_at,
        )
        for message in service.list_messages(conversation.id)
    ]
    base = conversation_response(conversation, len(messages))
    base_payload = base.model_dump() if hasattr(base, "model_dump") else base.dict()
    return PortalConversationDetailResponse(**base_payload, messages=messages)


@router.get("/widget", response_model=PortalWidgetResponse)
def get_widget_setup(
    portal_session: BusinessPortalSession = Depends(get_current_business_session),
    session: Session = Depends(get_db_session),
) -> PortalWidgetResponse:
    """Return widget setup details for the current tenant."""
    widget = BusinessPortalService(session, portal_session.tenant_id).active_widget()
    if widget is None:
        return PortalWidgetResponse(
            id=None,
            status="not_configured",
            key_prefix=None,
            embed_code=None,
            allowed_origins=None,
        )
    return widget_response(widget)


@router.post("/widget/keys", response_model=PortalWidgetResponse)
def create_widget_key(
    portal_session: BusinessPortalSession = Depends(get_current_business_session),
    session: Session = Depends(get_db_session),
) -> PortalWidgetResponse:
    """Create a new active widget key and return it once."""
    service = WidgetService(session)
    widget_key = service.generate_widget_key()
    widget = service.create_widget_config(
        tenant_id=portal_session.tenant_id,
        widget_key=widget_key,
        name=f"{portal_session.tenant_name} website widget",
    )
    session.commit()
    return widget_response(widget, widget_key=widget_key)


@router.get("/analytics", response_model=PortalAnalyticsResponse)
def get_analytics(
    portal_session: BusinessPortalSession = Depends(get_current_business_session),
    session: Session = Depends(get_db_session),
) -> PortalAnalyticsResponse:
    """Return basic current tenant analytics."""
    service = BusinessPortalService(session, portal_session.tenant_id)
    analytics = service.analytics()
    recent_usage = [
        {
            "event_type": event.event_type,
            "event_source": event.event_source,
            "attributes": event.attributes or {},
            "created_at": event.created_at.isoformat(),
        }
        for event in service.recent_usage()
    ]
    return PortalAnalyticsResponse(
        documents_total=analytics.documents_total,
        documents_ingested=analytics.documents_ingested,
        leads_total=analytics.leads_total,
        conversations_total=analytics.conversations_total,
        open_conversations=analytics.open_conversations,
        messages_total=analytics.messages_total,
        widget_status=analytics.widget_status,
        recent_usage=recent_usage,
    )


def lead_response(lead) -> PortalLeadResponse:
    """Map lead ORM model to response."""
    return PortalLeadResponse(
        id=lead.id,
        conversation_id=lead.conversation_id,
        customer_name=lead.customer_name,
        customer_email=lead.customer_email,
        customer_phone=lead.customer_phone,
        job_type=lead.job_type,
        suburb=lead.suburb,
        urgency=lead.urgency,
        status=lead.status,
        qualified_at=lead.qualified_at,
        qualification_reason=lead.qualification_reason,
        notification_status=lead.notification_status,
        last_notified_at=lead.last_notified_at,
        notes=lead.notes,
        created_at=lead.created_at,
    )


def conversation_response(conversation, message_count: int) -> PortalConversationResponse:
    """Map conversation ORM model to response."""
    return PortalConversationResponse(
        id=conversation.id,
        visitor_label=conversation.visitor_label,
        status=conversation.status,
        source=conversation.source,
        created_at=conversation.created_at,
        message_count=message_count,
    )


def widget_response(widget, widget_key: str | None = None) -> PortalWidgetResponse:
    """Map widget config to response."""
    display_key = widget_key or f"{widget.key_prefix}..."
    embed_code = (
        '<script src="./chat-widget.js" '
        'data-api-base-url="https://api.example.com" '
        f'data-widget-key="{display_key}" '
        'data-title="Ask our AI receptionist"></script>'
    )
    return PortalWidgetResponse(
        id=widget.id,
        status=widget.status,
        key_prefix=widget.key_prefix,
        widget_key=widget_key,
        embed_code=embed_code,
        allowed_origins=widget.allowed_origins,
    )
