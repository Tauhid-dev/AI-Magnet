"""Tenant-scoped usage logging service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.usage import GlobalAuditLog, UsageLog
from app.usage.taxonomy import UsageEventSource, UsageEventType


class UsageService:
    """Record analytics-safe usage events."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def record_event(
        self,
        *,
        tenant_id: str,
        event_type: str,
        event_source: str | None = None,
        attributes: dict | None = None,
    ) -> UsageLog:
        """Persist one tenant-scoped usage event with safe attributes."""
        event = UsageLog(
            tenant_id=tenant_id,
            event_type=event_type,
            event_source=event_source,
            attributes=attributes or {},
        )
        self.session.add(event)
        self.session.flush()
        return event

    def record_rate_limit_exceeded(
        self,
        *,
        tenant_id: str | None,
        event_source: str | None,
        attributes: dict | None = None,
    ) -> UsageLog | GlobalAuditLog:
        """Persist a privacy-safe rate-limit abuse analytics event."""
        payload = attributes or {}
        if tenant_id:
            return self.record_event(
                tenant_id=tenant_id,
                event_type=UsageEventType.RATE_LIMIT_EXCEEDED,
                event_source=event_source,
                attributes=payload,
            )
        if event_source:
            payload = {**payload, "event_source": event_source}
        event = GlobalAuditLog(
            actor_id=None,
            action=UsageEventType.RATE_LIMIT_EXCEEDED,
            target_type="rate_limit",
            attributes=payload,
        )
        self.session.add(event)
        self.session.flush()
        return event

    def record_chat_event(
        self,
        *,
        tenant_id: str,
        event_type: str,
        conversation_id: str,
        attributes: dict | None = None,
    ) -> UsageLog:
        """Record a chat/widget usage event."""
        payload = {"conversation_id": conversation_id}
        if attributes:
            payload.update(attributes)
        return self.record_event(
            tenant_id=tenant_id,
            event_type=event_type,
            event_source=UsageEventSource.CHAT_WIDGET,
            attributes=payload,
        )

    def record_document_ingestion(
        self,
        *,
        tenant_id: str,
        document_id: str,
        status: str,
        chunk_count: int,
    ) -> UsageLog:
        """Record document ingestion completion without raw document content."""
        event_type = (
            UsageEventType.DOCUMENT_INGESTED
            if status == "ingested"
            else UsageEventType.DOCUMENT_INGESTION_FAILED
        )
        return self.record_event(
            tenant_id=tenant_id,
            event_type=event_type,
            event_source=UsageEventSource.RAG_INGESTION,
            attributes={
                "document_id": document_id,
                "status": status,
                "chunk_count": chunk_count,
            },
        )
