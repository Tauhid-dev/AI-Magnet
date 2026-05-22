"""Worker-style RAG ingestion entrypoint."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.providers.ai.base import EmbeddingProvider
from app.rag.ingestion import RagIngestionService


def ingest_document_job(
    session: Session,
    embedding_provider: EmbeddingProvider,
    tenant_id: str,
    filename: str,
    content: bytes,
    content_type: str | None = "text/plain",
    storage_path: str | None = None,
) -> str:
    """Run document ingestion and return the document id."""
    document = RagIngestionService(session, embedding_provider).ingest_bytes(
        tenant_id=tenant_id,
        filename=filename,
        content=content,
        content_type=content_type,
        storage_path=storage_path,
    )
    return document.id
