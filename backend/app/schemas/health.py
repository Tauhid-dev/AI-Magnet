"""Schemas for health endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str
    service: str
    environment: str
    version: str
