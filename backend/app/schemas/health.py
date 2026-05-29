"""Schemas for health endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str
    service: str
    environment: str
    version: str


class ReadinessResponse(HealthResponse):
    """Readiness response for load balancers and release smoke tests."""

    database: str
    configuration: str
    rate_limiting: str
    admin_security: str
    checks: dict[str, str]
