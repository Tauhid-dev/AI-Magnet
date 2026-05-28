"""Background job processing loop helpers."""

from __future__ import annotations

import logging
import os
import socket
from collections.abc import Mapping

from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.jobs.handlers import (
    JobHandler,
    PermanentJobError,
    RetryableJobError,
    get_default_handlers,
)
from app.jobs.service import BackgroundJobService
from app.models.job import BackgroundJob


logger = logging.getLogger(__name__)


class BackgroundJobProcessor:
    """Claim and execute one durable job at a time."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        settings: Settings | None = None,
        worker_id: str | None = None,
        handlers: Mapping[str, JobHandler] | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.settings = settings or get_settings()
        self.worker_id = worker_id or default_worker_id()
        self.handlers = handlers or get_default_handlers()

    def process_one(self) -> BackgroundJob | None:
        """Process one due job, returning the job if work was attempted."""
        with self.session_factory() as session:
            service = BackgroundJobService(session, self.settings)
            service.reset_stale_running_jobs(self.settings.worker_queue_name)
            job = service.acquire_due_job(
                queue_name=self.settings.worker_queue_name,
                worker_id=self.worker_id,
            )
            if job is None:
                service.upsert_worker_heartbeat(
                    worker_id=self.worker_id,
                    queue_name=self.settings.worker_queue_name,
                    status="idle",
                    pid=os.getpid(),
                    hostname=socket.gethostname(),
                )
                session.commit()
                return None
            job_id = job.id
            service.upsert_worker_heartbeat(
                worker_id=self.worker_id,
                queue_name=self.settings.worker_queue_name,
                status="running",
                current_job_id=job.id,
                pid=os.getpid(),
                hostname=socket.gethostname(),
            )
            session.commit()

        with self.session_factory() as session:
            service = BackgroundJobService(session, self.settings)
            job = service.get_job(job_id)
            if job is None:
                return None
            handler = self.handlers.get(job.job_type)
            try:
                if handler is None:
                    raise PermanentJobError(f"No handler registered for {job.job_type}")
                logger.info("Processing background job %s (%s)", job.id, job.job_type)
                result = handler(session, job, self.settings)
            except PermanentJobError as exc:
                logger.warning("Background job %s failed permanently: %s", job.id, exc)
                service.mark_failed(job, exc, permanent=True)
            except RetryableJobError as exc:
                logger.warning("Background job %s scheduled for retry: %s", job.id, exc)
                service.mark_failed(job, exc)
            except Exception as exc:
                logger.exception("Background job %s failed with unexpected error", job.id)
                service.mark_failed(job, exc)
            else:
                service.mark_succeeded(job, result)
                logger.info("Background job %s completed", job.id)
            finally:
                service.upsert_worker_heartbeat(
                    worker_id=self.worker_id,
                    queue_name=self.settings.worker_queue_name,
                    status="idle",
                    pid=os.getpid(),
                    hostname=socket.gethostname(),
                )
                session.commit()
            return job

    def mark_stopping(self, status: str = "stopped") -> None:
        """Persist worker shutdown state."""
        with self.session_factory() as session:
            BackgroundJobService(session, self.settings).upsert_worker_heartbeat(
                worker_id=self.worker_id,
                queue_name=self.settings.worker_queue_name,
                status=status,
                pid=os.getpid(),
                hostname=socket.gethostname(),
            )
            session.commit()


def default_worker_id() -> str:
    """Create a readable worker id."""
    return f"{socket.gethostname()}:{os.getpid()}"
