"""Public website widget API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.rate_limit import enforce_rate_limit
from app.db.session import get_db_session
from app.schemas.widget import WidgetInitRequest, WidgetInitResponse
from app.widget.service import WidgetService


router = APIRouter(prefix="/widget", tags=["widget"])


def get_widget_service(
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> WidgetService:
    """Return the widget service for request handling."""
    return WidgetService(session, settings)


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
