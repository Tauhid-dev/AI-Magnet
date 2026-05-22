"""Health check routes."""

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return service health and runtime context."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.environment,
        version=settings.app_version,
    )
