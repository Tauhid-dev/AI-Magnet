from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import Settings
from app.db.base import Base
from app.jobs.handlers import PermanentJobError, RetryableJobError
from app.jobs.processor import BackgroundJobProcessor
from app.jobs.service import (
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_RETRY_SCHEDULED,
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
