from datetime import timedelta
from threading import Barrier, Lock, Thread

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import Settings
from app.db.base import Base, utc_now
from app.jobs.handlers import PermanentJobError, RetryableJobError
from app.jobs.processor import BackgroundJobProcessor
from app.jobs.service import (
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_RETRY_SCHEDULED,
    JOB_STATUS_RUNNING,
    JOB_TYPE_RAG_DOCUMENT_INGESTION,
    BackgroundJobService,
)
from app.leads.workflow import LeadWorkflowService
from app.models import BackgroundJob, DocumentChunk, Lead, NotificationDelivery, UsageLog
from app.notifications.service import NotificationService
from app.rag.ingestion import RagIngestionService
from app.tenants.service import TenantService


class NoopWakeQueue:
    def notify(self, _job_id: str) -> bool:
        return True


def create_test_session_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True, expire_on_commit=False)


def create_file_test_session_factory(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'background-jobs.db'}",
        future=True,
        connect_args={"check_same_thread": False, "timeout": 10},
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True, expire_on_commit=False)


def acquire_jobs_concurrently(session_factory, settings, worker_ids):
    barrier = Barrier(len(worker_ids))
    lock = Lock()
    results = []
    errors = []

    def run(worker_id):
        try:
            barrier.wait(timeout=10)
            with session_factory() as session:
                job = BackgroundJobService(
                    session,
                    settings,
                    redis_wake_queue=NoopWakeQueue(),
                ).acquire_due_job(
                    queue_name=settings.worker_queue_name,
                    worker_id=worker_id,
                )
                claimed = (worker_id, job.id if job is not None else None)
                session.commit()
        except Exception as exc:  # pragma: no cover - surfaced by assertion below
            with lock:
                errors.append(exc)
        else:
            with lock:
                results.append(claimed)

    threads = [Thread(target=run, args=(worker_id,)) for worker_id in worker_ids]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not [thread for thread in threads if thread.is_alive()]
    assert errors == []
    return results


def test_acquire_due_job_claims_queued_job():
    session_factory = create_test_session_factory()
    settings = Settings()
    with session_factory() as session:
        job = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).enqueue("test.claim", {}, priority=10).job
        session.commit()
        job_id = job.id

    with session_factory() as session:
        claimed = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).acquire_due_job(
            queue_name=settings.worker_queue_name,
            worker_id="worker-a",
        )
        session.commit()

    assert claimed is not None
    assert claimed.id == job_id
    assert claimed.status == JOB_STATUS_RUNNING
    assert claimed.attempts == 1
    assert claimed.locked_by == "worker-a"
    assert claimed.locked_at is not None
    assert claimed.started_at is not None
    assert claimed.last_error is None


def test_acquire_due_job_claims_due_retry_scheduled_job():
    session_factory = create_test_session_factory()
    settings = Settings()
    with session_factory() as session:
        job = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).enqueue("test.retry", {}, max_attempts=3).job
        job.status = JOB_STATUS_RETRY_SCHEDULED
        job.scheduled_at = utc_now() - timedelta(seconds=1)
        job.attempts = 1
        job.last_error = "temporary outage"
        session.commit()
        job_id = job.id

    with session_factory() as session:
        claimed = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).acquire_due_job(
            queue_name=settings.worker_queue_name,
            worker_id="worker-b",
        )
        session.commit()

    assert claimed is not None
    assert claimed.id == job_id
    assert claimed.status == JOB_STATUS_RUNNING
    assert claimed.attempts == 2
    assert claimed.locked_by == "worker-b"
    assert claimed.last_error is None


def test_acquire_due_job_does_not_claim_non_eligible_jobs():
    session_factory = create_test_session_factory()
    settings = Settings()
    with session_factory() as session:
        service = BackgroundJobService(session, settings, redis_wake_queue=NoopWakeQueue())
        future_job = service.enqueue("test.future", {}).job
        future_job.scheduled_at = utc_now() + timedelta(minutes=5)
        running_job = service.enqueue("test.running", {}).job
        running_job.status = JOB_STATUS_RUNNING
        running_job.started_at = utc_now()
        running_job.locked_at = utc_now()
        running_job.locked_by = "worker-existing"
        retry_future_job = service.enqueue("test.retry.future", {}).job
        retry_future_job.status = JOB_STATUS_RETRY_SCHEDULED
        retry_future_job.scheduled_at = utc_now() + timedelta(minutes=5)
        completed_job = service.enqueue("test.completed", {}).job
        completed_job.status = JOB_STATUS_COMPLETED
        service.enqueue("test.other-queue", {}, queue_name="other").job
        session.commit()

    with session_factory() as session:
        claimed = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).acquire_due_job(
            queue_name=settings.worker_queue_name,
            worker_id="worker-c",
        )
        session.commit()

    assert claimed is None


def test_acquire_due_job_preserves_priority_then_schedule_order():
    session_factory = create_test_session_factory()
    settings = Settings()
    now = utc_now()
    with session_factory() as session:
        service = BackgroundJobService(session, settings, redis_wake_queue=NoopWakeQueue())
        later_high_priority = service.enqueue("test.later-high", {}, priority=1).job
        later_high_priority.scheduled_at = now + timedelta(seconds=10)
        earlier_low_priority = service.enqueue("test.earlier-low", {}, priority=50).job
        earlier_low_priority.scheduled_at = now - timedelta(seconds=10)
        earliest_same_priority = service.enqueue("test.earliest-same", {}, priority=1).job
        earliest_same_priority.scheduled_at = now - timedelta(seconds=5)
        session.commit()

    with session_factory() as session:
        claimed = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).acquire_due_job(
            queue_name=settings.worker_queue_name,
            worker_id="worker-order",
        )
        session.commit()

    assert claimed is not None
    assert claimed.job_type == "test.earliest-same"


def test_concurrent_workers_do_not_receive_same_job(tmp_path):
    session_factory = create_file_test_session_factory(tmp_path)
    settings = Settings()
    worker_ids = [f"worker-{index}" for index in range(6)]
    with session_factory() as session:
        job = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).enqueue("test.single-concurrent", {}).job
        session.commit()
        job_id = job.id

    results = acquire_jobs_concurrently(session_factory, settings, worker_ids)
    claimed_ids = [claimed_id for _worker_id, claimed_id in results if claimed_id is not None]

    assert claimed_ids == [job_id]
    with session_factory() as session:
        stored_job = session.get(BackgroundJob, job_id)
        assert stored_job.status == JOB_STATUS_RUNNING
        assert stored_job.attempts == 1
        assert stored_job.locked_by in worker_ids


def test_multiple_due_jobs_distribute_across_concurrent_workers(tmp_path):
    session_factory = create_file_test_session_factory(tmp_path)
    settings = Settings()
    worker_ids = [f"worker-{index}" for index in range(5)]
    with session_factory() as session:
        service = BackgroundJobService(session, settings, redis_wake_queue=NoopWakeQueue())
        expected_job_ids = {
            service.enqueue(f"test.concurrent-{index}", {}, priority=index).job.id
            for index in range(len(worker_ids))
        }
        session.commit()

    results = acquire_jobs_concurrently(session_factory, settings, worker_ids)
    claimed_ids = [claimed_id for _worker_id, claimed_id in results if claimed_id is not None]

    assert set(claimed_ids) == expected_job_ids
    assert len(claimed_ids) == len(set(claimed_ids)) == len(worker_ids)
    with session_factory() as session:
        jobs = list(session.scalars(select(BackgroundJob)))
        assert {job.locked_by for job in jobs} == set(worker_ids)
        assert {job.status for job in jobs} == {JOB_STATUS_RUNNING}
        assert {job.attempts for job in jobs} == {1}


def test_stale_running_job_is_recovered_and_can_be_reclaimed():
    session_factory = create_test_session_factory()
    settings = Settings(
        worker_job_lock_timeout_seconds=1,
        worker_retry_base_seconds=0,
        worker_retry_max_seconds=0,
    )
    with session_factory() as session:
        job = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).enqueue("test.stale", {}, max_attempts=3).job
        session.commit()
        job_id = job.id

    with session_factory() as session:
        service = BackgroundJobService(session, settings, redis_wake_queue=NoopWakeQueue())
        claimed = service.acquire_due_job(
            queue_name=settings.worker_queue_name,
            worker_id="worker-stale",
        )
        assert claimed is not None
        claimed.locked_at = utc_now() - timedelta(seconds=10)
        session.commit()

    with session_factory() as session:
        service = BackgroundJobService(session, settings, redis_wake_queue=NoopWakeQueue())
        assert service.reset_stale_running_jobs(settings.worker_queue_name) == 1
        session.commit()

    with session_factory() as session:
        recovered = session.get(BackgroundJob, job_id)
        assert recovered.status == JOB_STATUS_RETRY_SCHEDULED
        assert recovered.attempts == 1
        assert recovered.locked_at is None
        assert recovered.locked_by is None
        assert recovered.last_error == "Worker lock expired before completion"

    with session_factory() as session:
        reclaimed = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).acquire_due_job(
            queue_name=settings.worker_queue_name,
            worker_id="worker-reclaim",
        )
        session.commit()

    assert reclaimed is not None
    assert reclaimed.id == job_id
    assert reclaimed.status == JOB_STATUS_RUNNING
    assert reclaimed.attempts == 2
    assert reclaimed.locked_by == "worker-reclaim"


def test_document_ingestion_job_processes_and_redacts_sensitive_payload():
    session_factory = create_test_session_factory()
    settings = Settings(
        ai_provider="test",
        ai_embedding_dimensions=16,
        rag_chunk_size=6,
        rag_chunk_overlap=2,
    )
    with session_factory() as session:
        tenant = TenantService(session).create_tenant("Demo Plumbing", "demo-plumbing")
        document = RagIngestionService(
            session=session,
            embedding_provider=None,
            settings=settings,
        ).create_pending_document(
            tenant_id=tenant.id,
            filename="services.txt",
            content_type="text/plain",
        )
        enqueue_result = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).enqueue_document_ingestion(
            tenant_id=tenant.id,
            document_id=document.id,
            filename=document.filename,
            content="Emergency blocked drains and hot water repairs in Bondi",
            content_type=document.content_type,
        )
        duplicate_result = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).enqueue_document_ingestion(
            tenant_id=tenant.id,
            document_id=document.id,
            filename=document.filename,
            content="Emergency blocked drains and hot water repairs in Bondi",
            content_type=document.content_type,
        )
        session.commit()

    assert enqueue_result.created is True
    assert duplicate_result.created is False
    assert duplicate_result.job.id == enqueue_result.job.id

    processor = BackgroundJobProcessor(
        session_factory,
        settings=settings,
        worker_id="test-worker",
    )
    processed_job = processor.process_one()

    with session_factory() as session:
        job = session.get(BackgroundJob, processed_job.id)
        chunks = list(session.scalars(select(DocumentChunk)))
        usage = list(session.scalars(select(UsageLog)))

        assert job is not None
        assert job.status == JOB_STATUS_COMPLETED
        assert job.attempts == 1
        assert job.payload == {"redacted": True, "job_type": JOB_TYPE_RAG_DOCUMENT_INGESTION}
        assert job.result["status"] == "ingested"
        assert len(chunks) >= 2
        assert {event.event_type for event in usage} == {"document_ingested"}


def test_retryable_job_records_retry_then_completes(monkeypatch):
    monkeypatch.setattr("app.jobs.redis_queue.RedisWakeQueue.notify", lambda *_args: True)
    session_factory = create_test_session_factory()
    settings = Settings(worker_retry_base_seconds=0, worker_retry_max_seconds=0)
    calls = {"count": 0}

    def flaky_handler(_session, _job, _settings):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RetryableJobError("temporary outage")
        return {"ok": True}

    with session_factory() as session:
        job = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).enqueue(
            "test.flaky",
            {"safe": "payload"},
            idempotency_key="test.flaky:1",
            max_attempts=2,
        ).job
        session.commit()
        job_id = job.id

    processor = BackgroundJobProcessor(
        session_factory,
        settings=settings,
        worker_id="test-worker",
        handlers={"test.flaky": flaky_handler},
    )
    processor.process_one()
    with session_factory() as session:
        retry_job = session.get(BackgroundJob, job_id)
        assert retry_job.status == JOB_STATUS_RETRY_SCHEDULED
        assert retry_job.attempts == 1
        assert retry_job.last_error == "temporary outage"

    processor.process_one()
    with session_factory() as session:
        completed_job = session.get(BackgroundJob, job_id)
        assert completed_job.status == JOB_STATUS_COMPLETED
        assert completed_job.attempts == 2
        assert completed_job.result == {"ok": True}


def test_permanent_job_failure_is_visible_without_retry():
    session_factory = create_test_session_factory()
    settings = Settings()

    def failing_handler(_session, _job, _settings):
        raise PermanentJobError("bad input")

    with session_factory() as session:
        job = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).enqueue("test.permanent", {}, max_attempts=3).job
        session.commit()
        job_id = job.id

    BackgroundJobProcessor(
        session_factory,
        settings=settings,
        worker_id="test-worker",
        handlers={"test.permanent": failing_handler},
    ).process_one()

    with session_factory() as session:
        failed_job = session.get(BackgroundJob, job_id)
        assert failed_job.status == JOB_STATUS_FAILED
        assert failed_job.attempts == 1
        assert failed_job.last_error == "bad input"
        assert failed_job.failed_at is not None


def test_notification_delivery_job_sends_and_records_usage():
    session_factory = create_test_session_factory()
    settings = Settings(email_provider="console")
    with session_factory() as session:
        tenant = TenantService(session).create_tenant("Demo Plumbing", "demo-plumbing")
        TenantService(session).create_business(
            tenant_id=tenant.id,
            name="Demo Plumbing",
            email="owner@example.test",
        )
        lead = Lead(
            tenant_id=tenant.id,
            customer_name="Alex",
            customer_phone="0412 345 678",
            job_type="blocked drain",
            suburb="Bondi",
            urgency="today",
            status="new",
        )
        session.add(lead)
        LeadWorkflowService(session).evaluate_qualification(lead)
        delivery = NotificationService(session, settings=settings).queue_lead_notification(
            tenant.id,
            lead,
        ).delivery
        job = BackgroundJobService(
            session,
            settings,
            redis_wake_queue=NoopWakeQueue(),
        ).enqueue_notification_delivery(tenant_id=tenant.id, delivery_id=delivery.id).job
        session.commit()
        job_id = job.id
        delivery_id = delivery.id

    BackgroundJobProcessor(session_factory, settings=settings, worker_id="test-worker").process_one()

    with session_factory() as session:
        completed_job = session.get(BackgroundJob, job_id)
        stored_delivery = session.get(NotificationDelivery, delivery_id)
        usage_events = list(session.scalars(select(UsageLog)))

        assert completed_job.status == JOB_STATUS_COMPLETED
        assert stored_delivery.status == "sent"
        assert {event.event_type for event in usage_events} == {"lead_notification_sent"}
