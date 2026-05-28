"""Durable background job service."""

from __future__ import annotations

import math
import socket
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.base import utc_now
from app.jobs.redis_queue import RedisWakeQueue
from app.models.job import BackgroundJob, WorkerHeartbeat


JOB_STATUS_QUEUED = "queued"
JOB_STATUS_RUNNING = "running"
JOB_STATUS_RETRY_SCHEDULED = "retry_scheduled"
JOB_STATUS_COMPLETED = "completed"
JOB_STATUS_FAILED = "failed"
JOB_STATUS_CANCELLED = "cancelled"

ACTIVE_JOB_STATUSES = {
    JOB_STATUS_QUEUED,
    JOB_STATUS_RUNNING,
    JOB_STATUS_RETRY_SCHEDULED,
}
TERMINAL_JOB_STATUSES = {
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_CANCELLED,
}

JOB_TYPE_RAG_DOCUMENT_INGESTION = "rag.document_ingestion"
JOB_TYPE_RAG_WEBSITE_CRAWL = "rag.website_crawl"
JOB_TYPE_NOTIFICATION_DELIVERY = "notification.send_delivery"


@dataclass(frozen=True)
class EnqueueResult:
    """Result returned when requesting a background job."""

    job: BackgroundJob
    created: bool


class BackgroundJobService:
    """Create, inspect, and transition durable background jobs."""

    def __init__(
        self,
        session: Session,
        settings: Settings | None = None,
        redis_wake_queue: RedisWakeQueue | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.redis_wake_queue = redis_wake_queue or RedisWakeQueue(self.settings)

    def enqueue(
        self,
        job_type: str,
        payload: dict[str, Any],
        *,
        tenant_id: str | None = None,
        queue_name: str | None = None,
        idempotency_key: str | None = None,
        max_attempts: int | None = None,
        priority: int = 100,
        sensitive_payload: bool = False,
        notify_worker: bool = True,
    ) -> EnqueueResult:
        """Create a queued job or return the existing idempotent job."""
        if idempotency_key:
            existing = self.session.scalars(
                select(BackgroundJob).where(BackgroundJob.idempotency_key == idempotency_key)
            ).first()
            if existing is not None:
                if existing.status in ACTIVE_JOB_STATUSES and notify_worker:
                    self.redis_wake_queue.notify(existing.id)
                return EnqueueResult(existing, created=False)

        job = BackgroundJob(
            tenant_id=tenant_id,
            queue_name=queue_name or self.settings.worker_queue_name,
            job_type=job_type,
            payload=payload,
            idempotency_key=idempotency_key,
            max_attempts=max_attempts or self.settings.worker_default_max_attempts,
            priority=priority,
            scheduled_at=utc_now(),
            sensitive_payload=sensitive_payload,
        )
        self.session.add(job)
        self.session.flush()
        if notify_worker:
            self.redis_wake_queue.notify(job.id)
        return EnqueueResult(job, created=True)

    def enqueue_document_ingestion(
        self,
        *,
        tenant_id: str,
        document_id: str,
        filename: str,
        content: str,
        content_type: str | None,
    ) -> EnqueueResult:
        """Queue tenant document ingestion and embedding generation."""
        return self.enqueue(
            JOB_TYPE_RAG_DOCUMENT_INGESTION,
            {
                "document_id": document_id,
                "filename": filename,
                "content": content,
                "content_type": content_type,
            },
            tenant_id=tenant_id,
            idempotency_key=f"{JOB_TYPE_RAG_DOCUMENT_INGESTION}:{tenant_id}:{document_id}",
            sensitive_payload=True,
        )

    def enqueue_notification_delivery(
        self,
        *,
        tenant_id: str,
        delivery_id: str,
    ) -> EnqueueResult:
        """Queue one tenant-owned notification delivery send attempt."""
        return self.enqueue(
            JOB_TYPE_NOTIFICATION_DELIVERY,
            {"delivery_id": delivery_id},
            tenant_id=tenant_id,
            idempotency_key=f"{JOB_TYPE_NOTIFICATION_DELIVERY}:{tenant_id}:{delivery_id}",
        )

    def enqueue_website_crawl(
        self,
        *,
        tenant_id: str,
        source_id: str,
    ) -> EnqueueResult:
        """Queue tenant website/sitemap crawl and indexing work."""
        return self.enqueue(
            JOB_TYPE_RAG_WEBSITE_CRAWL,
            {"source_id": source_id},
            tenant_id=tenant_id,
            sensitive_payload=False,
        )

    def get_job(self, job_id: str) -> BackgroundJob | None:
        """Return a job by id."""
        return self.session.get(BackgroundJob, job_id)

    def get_tenant_job(self, tenant_id: str, job_id: str) -> BackgroundJob | None:
        """Return one tenant-owned job by id."""
        return self.session.scalars(
            select(BackgroundJob).where(
                BackgroundJob.id == job_id,
                BackgroundJob.tenant_id == tenant_id,
            )
        ).first()

    def list_tenant_jobs(self, tenant_id: str, limit: int = 50) -> list[BackgroundJob]:
        """Return recent tenant-owned jobs."""
        return list(
            self.session.scalars(
                select(BackgroundJob)
                .where(BackgroundJob.tenant_id == tenant_id)
                .order_by(BackgroundJob.created_at.desc())
                .limit(limit)
            )
        )

    def list_jobs(self, limit: int = 100) -> list[BackgroundJob]:
        """Return recent jobs across tenants for super admins."""
        return list(
            self.session.scalars(
                select(BackgroundJob).order_by(BackgroundJob.created_at.desc()).limit(limit)
            )
        )

    def acquire_due_job(
        self,
        *,
        queue_name: str,
        worker_id: str,
    ) -> BackgroundJob | None:
        """Mark the next due queued/retry job as running for this worker."""
        now = utc_now()
        statement = (
            select(BackgroundJob)
            .where(
                BackgroundJob.queue_name == queue_name,
                BackgroundJob.status.in_([JOB_STATUS_QUEUED, JOB_STATUS_RETRY_SCHEDULED]),
                BackgroundJob.scheduled_at <= now,
            )
            .order_by(BackgroundJob.priority.asc(), BackgroundJob.scheduled_at.asc())
            .limit(1)
        )
        job = self.session.scalars(statement).first()
        if job is None:
            return None
        job.status = JOB_STATUS_RUNNING
        job.locked_by = worker_id
        job.locked_at = now
        job.started_at = now
        job.attempts += 1
        job.last_error = None
        self.session.flush()
        return job

    def mark_succeeded(
        self,
        job: BackgroundJob,
        result: dict[str, Any] | None = None,
    ) -> BackgroundJob:
        """Mark a job complete and clear lock metadata."""
        now = utc_now()
        job.status = JOB_STATUS_COMPLETED
        job.completed_at = now
        job.failed_at = None
        job.locked_at = None
        job.locked_by = None
        job.last_error = None
        job.result = result or {}
        if job.sensitive_payload:
            job.payload = {"redacted": True, "job_type": job.job_type}
        self.session.flush()
        return job

    def mark_failed(
        self,
        job: BackgroundJob,
        error: Exception | str,
        *,
        permanent: bool = False,
    ) -> BackgroundJob:
        """Record a failure, scheduling retry unless attempts are exhausted."""
        now = utc_now()
        error_message = str(error)[:2000]
        final_failure = permanent or job.attempts >= job.max_attempts
        job.locked_at = None
        job.locked_by = None
        job.last_error = error_message
        if final_failure:
            job.status = JOB_STATUS_FAILED
            job.failed_at = now
            job.scheduled_at = None
            if job.sensitive_payload:
                job.payload = {"redacted": True, "job_type": job.job_type}
        else:
            job.status = JOB_STATUS_RETRY_SCHEDULED
            job.scheduled_at = now + timedelta(seconds=self.retry_delay_seconds(job.attempts))
        self.session.flush()
        if not final_failure:
            self.redis_wake_queue.notify(job.id)
        return job

    def retry_delay_seconds(self, attempts: int) -> int:
        """Return bounded exponential retry delay in seconds."""
        base = max(self.settings.worker_retry_base_seconds, 0)
        if base == 0:
            return 0
        delay = base * int(math.pow(2, max(attempts - 1, 0)))
        return min(delay, self.settings.worker_retry_max_seconds)

    def reset_stale_running_jobs(self, queue_name: str) -> int:
        """Return stale running jobs to retry visibility after worker interruption."""
        cutoff = utc_now() - timedelta(seconds=self.settings.worker_job_lock_timeout_seconds)
        jobs = list(
            self.session.scalars(
                select(BackgroundJob).where(
                    BackgroundJob.queue_name == queue_name,
                    BackgroundJob.status == JOB_STATUS_RUNNING,
                    BackgroundJob.locked_at <= cutoff,
                )
            )
        )
        for job in jobs:
            self.mark_failed(job, "Worker lock expired before completion")
        self.session.flush()
        return len(jobs)

    def upsert_worker_heartbeat(
        self,
        *,
        worker_id: str,
        queue_name: str,
        status: str,
        current_job_id: str | None = None,
        pid: int | None = None,
        hostname: str | None = None,
    ) -> WorkerHeartbeat:
        """Update worker liveness state."""
        now = utc_now()
        heartbeat = self.session.get(WorkerHeartbeat, worker_id)
        if heartbeat is None:
            heartbeat = WorkerHeartbeat(
                worker_id=worker_id,
                queue_name=queue_name,
                status=status,
                hostname=hostname or socket.gethostname(),
                pid=pid,
                current_job_id=current_job_id,
                last_seen_at=now,
            )
            self.session.add(heartbeat)
        else:
            heartbeat.queue_name = queue_name
            heartbeat.status = status
            heartbeat.hostname = hostname or heartbeat.hostname
            heartbeat.pid = pid if pid is not None else heartbeat.pid
            heartbeat.current_job_id = current_job_id
            heartbeat.last_seen_at = now
            if status in {"stopping", "stopped"} and heartbeat.stopping_at is None:
                heartbeat.stopping_at = now
        self.session.flush()
        return heartbeat

    def list_worker_heartbeats(self, limit: int = 50) -> list[WorkerHeartbeat]:
        """Return recent worker heartbeat rows."""
        return list(
            self.session.scalars(
                select(WorkerHeartbeat)
                .order_by(WorkerHeartbeat.last_seen_at.desc())
                .limit(limit)
            )
        )
