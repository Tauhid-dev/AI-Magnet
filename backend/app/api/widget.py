"""Public website widget API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.rate_limit import enforce_rate_limit
from app.db.session import get_db_session
from app.schemas.widget import WidgetInitRequest, WidgetInitResponse
from app.usage import UsageEventSource
from app.widget.service import WidgetService


router = APIRouter(prefix="/widget", tags=["widget"])


def get_widget_service(
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> WidgetService:
    """Return the widget service for request handling."""
    return WidgetService(session, settings)


def resolve_widget_tenant_id(
    widget_service: WidgetService,
    widget_key: str,
    origin: str | None,
) -> str | None:
    """Resolve widget tenant attribution only after a rate-limit denial."""
    resolution = widget_service.resolve_widget_key(widget_key, origin)
    return resolution.tenant_id if resolution else None


@router.post("/init", response_model=WidgetInitResponse)
def initialize_widget(
    request: Request,
    payload: WidgetInitRequest,
    settings: Settings = Depends(get_settings),
    widget_service: WidgetService = Depends(get_widget_service),
) -> WidgetInitResponse:
    """Validate a public widget key without exposing tenant identifiers."""
    enforce_rate_limit(
        request,
        settings,
        scope="widget_init",
        identifiers=[payload.widget_key[:16]],
        limit=settings.rate_limit_widget_init_per_minute,
        session=widget_service.session,
        tenant_id_resolver=lambda: resolve_widget_tenant_id(
            widget_service,
            payload.widget_key,
            payload.origin,
        ),
        event_source=UsageEventSource.CHAT_WIDGET,
        actor_category="chat_widget",
    )
    resolution = widget_service.resolve_widget_key(payload.widget_key, payload.origin)
    if resolution is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive widget key",
        )
    return WidgetInitResponse(
        widget_key_prefix=resolution.widget.key_prefix,
        widget_name=resolution.widget.name,
        status=resolution.widget.status,
    )
