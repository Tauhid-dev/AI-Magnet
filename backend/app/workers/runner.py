"""Minimal worker process entrypoint for local deployment wiring."""

from __future__ import annotations

import logging
import signal
import time

from app.core.config import get_settings
from app.core.logging import configure_logging


def run() -> None:
    """Run a small long-lived worker process until stopped.

    The MVP currently performs ingestion and notification work synchronously.
    This process gives Docker Compose a stable worker service to attach future
    retryable jobs to without introducing a queue framework before it is needed.
    """
    settings = get_settings()
    settings.validate_runtime_security()
    configure_logging(settings.log_level)
    logger = logging.getLogger("app.workers.runner")
    should_stop = False

    def handle_stop(_signum, _frame) -> None:
        nonlocal should_stop
        should_stop = True

    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)
    logger.info("Worker process started in %s mode", settings.environment)
    while not should_stop:
        time.sleep(5)
    logger.info("Worker process stopped")


if __name__ == "__main__":
    run()
