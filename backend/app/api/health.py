"""Health check routes."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.schemas.health import HealthResponse, ReadinessResponse


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


@router.get("/ready", response_model=ReadinessResponse)
def readiness_check(
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_db_session),
) -> ReadinessResponse:
    """Return readiness state for database and runtime configuration."""
    checks: dict[str, str] = {}
    database = "ok"
    configuration = "ok"
    status = "ok"
    try:
        session.execute(text("SELECT 1"))
        checks["database_connectivity"] = "pass"
    except Exception:
        database = "error"
        status = "degraded"
        checks["database_connectivity"] = "fail"
    config_issues = settings.production_security_issues()
    if config_issues:
        configuration = "error"
        status = "degraded"
        checks["production_configuration"] = "fail"
    else:
        checks["production_configuration"] = "pass"
    checks["error_reporting_seam"] = "configured" if settings.error_reporting_dsn else "not_configured"
    return ReadinessResponse(
        status=status,
        service=settings.app_name,
        environment=settings.environment,
        version=settings.app_version,
        database=database,
        configuration=configuration,
        checks=checks,
    )
