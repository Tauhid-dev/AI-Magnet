"""Logging setup for the backend service."""

from __future__ import annotations

import logging


def configure_logging(log_level: str = "INFO") -> None:
    """Configure basic structured-enough logging for local and container runs."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,
    )
