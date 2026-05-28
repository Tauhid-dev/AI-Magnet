"""Widget API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class WidgetInitRequest(BaseModel):
    """Request to initialize the public widget."""

    widget_key: str = Field(min_length=12, max_length=256)
    origin: str | None = Field(default=None, max_length=500)


class WidgetInitResponse(BaseModel):
    """Safe widget initialization response."""

    widget_key_prefix: str
    widget_name: str
    status: str
