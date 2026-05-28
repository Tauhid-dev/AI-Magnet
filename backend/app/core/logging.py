"""Logging setup for the backend service."""

from __future__ import annotations

import contextvars
import json
import logging
from datetime import datetime, timezone
from typing import Any


request_id_context: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id",
    default="-",
)


class RequestIdFilter(logging.Filter):
    """Attach the current request ID to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True


class JsonFormatter(logging.Formatter):
    """Small JSON formatter for container logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"))


def bind_request_id(request_id: str) -> contextvars.Token[str]:
    """Bind a request ID for the lifetime of an HTTP request."""
    return request_id_context.set(request_id)


def reset_request_id(token: contextvars.Token[str]) -> None:
    """Reset the request ID context after request processing."""
    request_id_context.reset(token)


def configure_logging(log_level: str = "INFO", log_format: str = "text") -> None:
    """Configure logging for local and container runs."""
    handler = logging.StreamHandler()
    handler.addFilter(RequestIdFilter())
    if log_format.strip().lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s [request_id=%(request_id)s] %(message)s",
            )
        )
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        handlers=[handler],
        force=True,
    )
