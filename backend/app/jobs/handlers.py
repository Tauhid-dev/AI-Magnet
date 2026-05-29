"""Background job handlers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.jobs.service import (
    JOB_TYPE_NOTIFICATION_DELIVERY,
    JOB_TYPE_RAG_DOCUMENT_FILE_INGESTION,
    JOB_TYPE_RAG_DOCUMENT_INGESTION,
    JOB_TYPE_RAG_WEBSITE_CRAWL,
)
from app.models.job import BackgroundJob
from app.models.knowledge import KnowledgeDocument
from app.models.notification import NotificationDelivery
from app.notifications.service import (
    NOTIFICATION_STATUS_FAILED,
    NOTIFICATION_STATUS_RETRY_SCHEDULED,
    NOTIFICATION_STATUS_SENT,
    NotificationService,
)
from app.providers.ai.factory import get_embedding_provider
from app.rag.document_storage import DocumentStorageError, LocalDocumentStorage
from app.rag.ingestion import RagIngestionService
from app.rag.website_ingestion import WebsiteIngestionService
from app.usage import UsageEventSource, UsageEventType, UsageService


JobHandler = Callable[[Session, BackgroundJob, Settings], dict[str, Any]]


class RetryableJobError(RuntimeError):
    """Failure that should retry until job attempts are exhausted."""


class PermanentJobError(RuntimeError):
    """Failure that should not be retried."""


def get_default_handlers() -> Mapping[str, JobHandler]:
    """Return production job handlers by job type."""
    return {
        JOB_TYPE_RAG_DOCUMENT_INGESTION: handle_document_ingestion,
        JOB_TYPE_RAG_DOCUMENT_FILE_INGESTION: handle_document_file_ingestion,
        JOB_TYPE_RAG_WEBSITE_CRAWL: handle_website_crawl,
        JOB_TYPE_NOTIFICATION_DELIVERY: handle_notification_delivery,
    }


def handle_document_ingestion(
    session: Session,
    job: BackgroundJob,
    settings: Settings,
) -> dict[str, Any]:
    """Process a queued text/Markdown document into tenant-scoped chunks."""
    tenant_id = require_tenant(job)
    document_id = require_payload_string(job, "document_id")
    content = require_payload_string(job, "content")
    content_type = job.payload.get("content_type") or "text/plain"
    document = session.get(KnowledgeDocument, document_id)
    if document is None or document.tenant_id != tenant_id:
        raise PermanentJobError("Document does not exist for this tenant")
    if document.status == "ingested":
        return {"document_id": document.id, "status": document.status, "already_processed": True}
    try:
        RagIngestionService(
            session=session,
            embedding_provider=get_embedding_provider(settings),
            settings=settings,
        ).process_document_bytes(
            document=document,
            content=content.encode("utf-8"),
            content_type=str(content_type),
            raise_on_failure=True,
        )
    except ValueError as exc:
        UsageService(session).record_document_ingestion(
            tenant_id=tenant_id,
            document_id=document.id,
            status=document.status,
            chunk_count=0,
        )
        raise PermanentJobError(str(exc)) from exc
    chunk_count = len(document.chunks)
    UsageService(session).record_document_ingestion(
        tenant_id=tenant_id,
        document_id=document.id,
        status=document.status,
        chunk_count=chunk_count,
    )
    return {"document_id": document.id, "status": document.status, "chunk_count": chunk_count}


def handle_document_file_ingestion(
    session: Session,
    job: BackgroundJob,
    settings: Settings,
) -> dict[str, Any]:
    """Process a queued private uploaded document into tenant-scoped chunks."""
    tenant_id = require_tenant(job)
    document_id = require_payload_string(job, "document_id")
    document = session.get(KnowledgeDocument, document_id)
    if document is None or document.tenant_id != tenant_id:
        raise PermanentJobError("Document does not exist for this tenant")
    if not document.storage_path:
        document.status = "failed"
        document.extraction_status = "failed"
        document.error_message = "Uploaded document storage path is missing"
        raise PermanentJobError(document.error_message)
    try:
        content = LocalDocumentStorage(settings).read(document.storage_path)
        RagIngestionService(
            session=session,
            embedding_provider=get_embedding_provider(settings),
            settings=settings,
        ).process_document_bytes(
            document=document,
            content=content,
            content_type=document.content_type,
            raise_on_failure=True,
        )
    except (DocumentStorageError, FileNotFoundError, ValueError) as exc:
        UsageService(session).record_document_ingestion(
            tenant_id=tenant_id,
            document_id=document.id,
            status=document.status,
            chunk_count=0,
        )
        raise PermanentJobError(str(exc)) from exc
    chunk_count = len(document.chunks)
    UsageService(session).record_document_ingestion(
        tenant_id=tenant_id,
        document_id=document.id,
        status=document.status,
        chunk_count=chunk_count,
    )
    return {"document_id": document.id, "status": document.status, "chunk_count": chunk_count}


def handle_notification_delivery(
    session: Session,
    job: BackgroundJob,
    settings: Settings,
) -> dict[str, Any]:
    """Send one queued notification delivery."""
    tenant_id = require_tenant(job)
    delivery_id = require_payload_string(job, "delivery_id")
    delivery = session.get(NotificationDelivery, delivery_id)
    if delivery is None or delivery.tenant_id != tenant_id:
        raise PermanentJobError("Notification delivery does not exist for this tenant")
    if delivery.status == NOTIFICATION_STATUS_SENT:
        return {"delivery_id": delivery.id, "status": delivery.status, "already_processed": True}

    NotificationService(session, settings=settings).send_delivery(delivery)
    if delivery.status == NOTIFICATION_STATUS_SENT:
        UsageService(session).record_event(
            tenant_id=tenant_id,
            event_type=UsageEventType.LEAD_NOTIFICATION_SENT,
            event_source=UsageEventSource.NOTIFICATION_WORKFLOW,
            attributes={"delivery_id": delivery.id, "lead_id": delivery.lead_id},
        )
        return {"delivery_id": delivery.id, "status": delivery.status}
    if delivery.status == NOTIFICATION_STATUS_RETRY_SCHEDULED:
        raise RetryableJobError(delivery.error_message or "Notification delivery retry scheduled")
    if delivery.status == NOTIFICATION_STATUS_FAILED:
        raise PermanentJobError(delivery.error_message or "Notification delivery failed")
    raise RetryableJobError(f"Notification delivery ended in unexpected status {delivery.status}")


def handle_website_crawl(
    session: Session,
    job: BackgroundJob,
    settings: Settings,
) -> dict[str, Any]:
    """Crawl a tenant-approved website/sitemap source and ingest pages."""
    tenant_id = require_tenant(job)
    source_id = require_payload_string(job, "source_id")
    try:
        result = WebsiteIngestionService(
            session=session,
            settings=settings,
            embedding_provider=get_embedding_provider(settings),
        ).process_source(tenant_id=tenant_id, source_id=source_id)
    except ValueError as exc:
        UsageService(session).record_event(
            tenant_id=tenant_id,
            event_type=UsageEventType.WEBSITE_CRAWL_FAILED,
            event_source=UsageEventSource.RAG_INGESTION,
            attributes={"source_id": source_id, "error_type": exc.__class__.__name__},
        )
        raise PermanentJobError(str(exc)) from exc
    UsageService(session).record_event(
        tenant_id=tenant_id,
        event_type=UsageEventType.WEBSITE_CRAWL_COMPLETED,
        event_source=UsageEventSource.RAG_INGESTION,
        attributes={
            "source_id": result.source_id,
            "status": result.status,
            "pages_discovered": result.pages_discovered,
            "pages_ingested": result.pages_ingested,
            "pages_failed": result.pages_failed,
            "pages_skipped": result.pages_skipped,
        },
    )
    return {
        "source_id": result.source_id,
        "status": result.status,
        "pages_discovered": result.pages_discovered,
        "pages_ingested": result.pages_ingested,
        "pages_failed": result.pages_failed,
        "pages_skipped": result.pages_skipped,
    }


def require_tenant(job: BackgroundJob) -> str:
    """Return required tenant id for tenant-owned jobs."""
    if not job.tenant_id:
        raise PermanentJobError("Tenant-owned job is missing tenant_id")
    return job.tenant_id


def require_payload_string(job: BackgroundJob, key: str) -> str:
    """Read a non-empty string from a job payload."""
    value = job.payload.get(key)
    if not isinstance(value, str) or not value:
        raise PermanentJobError(f"Job payload is missing {key}")
    return value
