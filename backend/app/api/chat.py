"""Public chat conversation API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.chat.service import ChatService
from app.core.config import Settings, get_settings
from app.core.rate_limit import enforce_rate_limit
from app.db.session import get_db_session
from app.providers.ai.base import ChatCompletionProvider, EmbeddingProvider
from app.providers.ai.factory import get_chat_completion_provider, get_embedding_provider
from app.rag.retrieval import RagRetrievalService
from app.schemas.chat import (
    ConversationMessageRequest,
    ConversationMessageResponse,
    ConversationStartRequest,
    ConversationStartResponse,
    LeadCaptureState,
)
from app.widget.service import WidgetService


router = APIRouter(prefix="/chat", tags=["chat"])


def get_embedding_provider_dependency(
    settings: Settings = Depends(get_settings),
) -> EmbeddingProvider:
    """Return configured embedding provider."""
    return get_embedding_provider(settings)


def get_chat_completion_provider_dependency(
    settings: Settings = Depends(get_settings),
) -> ChatCompletionProvider:
    """Return configured chat provider."""
    return get_chat_completion_provider(settings)


def get_chat_service(
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider_dependency),
    chat_provider: ChatCompletionProvider = Depends(get_chat_completion_provider_dependency),
) -> ChatService:
    """Return the chat service for request handling."""
    retrieval_service = RagRetrievalService(session, embedding_provider)
    return ChatService(
        session=session,
        retrieval_service=retrieval_service,
        chat_provider=chat_provider,
        settings=settings,
    )


def get_widget_service(
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> WidgetService:
    """Return the widget service for request handling."""
    return WidgetService(session, settings)


@router.post("/conversations", response_model=ConversationStartResponse)
def start_conversation(
    request: Request,
    payload: ConversationStartRequest,
    settings: Settings = Depends(get_settings),
    widget_service: WidgetService = Depends(get_widget_service),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationStartResponse:
    """Start a tenant-scoped widget conversation."""
    enforce_rate_limit(
        request,
        settings,
        scope="chat_start_public",
        identifiers=[payload.widget_key[:16]],
        limit=settings.rate_limit_chat_start_per_minute,
    )
    resolution = widget_service.resolve_widget_key(payload.widget_key, payload.origin)
    if resolution is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive widget key",
        )
    enforce_rate_limit(
        request,
        settings,
        scope="chat_start_tenant_widget",
        identifiers=[resolution.tenant_id, resolution.widget.id],
        limit=settings.rate_limit_chat_start_per_minute,
    )
    result = chat_service.start_conversation(
        widget_resolution=resolution,
        visitor_label=payload.visitor_label,
    )
    return ConversationStartResponse(
        conversation_id=result.conversation.id,
        status=result.conversation.status,
        widget_key_prefix=result.widget_key_prefix,
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ConversationMessageResponse,
)
def post_conversation_message(
    request: Request,
    conversation_id: str,
    payload: ConversationMessageRequest,
    settings: Settings = Depends(get_settings),
    widget_service: WidgetService = Depends(get_widget_service),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationMessageResponse:
    """Store a visitor message and return a tenant-scoped AI answer."""
    enforce_rate_limit(
        request,
        settings,
        scope="chat_message_public",
        identifiers=[payload.widget_key[:16], conversation_id],
        limit=settings.rate_limit_chat_message_per_minute,
    )
    resolution = widget_service.resolve_widget_key(payload.widget_key, payload.origin)
    if resolution is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive widget key",
        )
    enforce_rate_limit(
        request,
        settings,
        scope="chat_message_tenant_widget",
        identifiers=[resolution.tenant_id, resolution.widget.id],
        limit=settings.rate_limit_chat_message_per_minute,
    )
    result = chat_service.handle_visitor_message(
        widget_resolution=resolution,
        conversation_id=conversation_id,
        message=payload.message,
        lead_fields=payload.lead,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found for widget tenant",
        )
    return ConversationMessageResponse(
        conversation_id=result.conversation.id,
        visitor_message_id=result.visitor_message.id,
        assistant_message_id=result.assistant_message.id,
        assistant_message=result.assistant_message.content,
        retrieved_chunk_count=len(result.retrieved_results),
        lead_capture=LeadCaptureState(
            lead_id=result.lead_capture.lead.id if result.lead_capture.lead else None,
            captured_fields=result.lead_capture.captured_fields,
            missing_fields=result.lead_capture.missing_fields,
            next_prompt=result.lead_capture.next_prompt,
        ),
    )
