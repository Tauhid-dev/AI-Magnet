"""Background worker process entrypoint."""

from __future__ import annotations

import logging
import signal

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import get_session_factory_for_url
from app.jobs.processor import BackgroundJobProcessor
from app.jobs.redis_queue import RedisWakeQueue


def run() -> None:
    """Run the durable job worker until stopped."""
    settings = get_settings()
    settings.validate_runtime_security()
    configure_logging(settings.log_level, settings.log_format)
    logger = logging.getLogger("app.workers.runner")
    should_stop = False

    def handle_stop(_signum, _frame) -> None:
        nonlocal should_stop
        should_stop = True

    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)
    session_factory = get_session_factory_for_url(settings.database_url, settings.debug)
    processor = BackgroundJobProcessor(session_factory, settings=settings)
    redis_queue = RedisWakeQueue(settings)
    logger.info(
        "Worker process started in %s mode on queue %s",
        settings.environment,
        settings.worker_queue_name,
    )
    while not should_stop:
        processed_job = processor.process_one()
        if should_stop:
            break
        if processed_job is None:
            redis_queue.wait(settings.worker_poll_interval_seconds)
    processor.mark_stopping()
    logger.info("Worker process stopped")


if __name__ == "__main__":
    run()
