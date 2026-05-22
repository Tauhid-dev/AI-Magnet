"""Tenant-scoped RAG ingestion service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.knowledge import DocumentChunk, KnowledgeDocument
from app.providers.ai.base import EmbeddingProvider
from app.rag.chunking import chunk_text
from app.rag.extraction import extract_text


class RagIngestionService:
    """Ingest tenant knowledge documents into chunks and embeddings."""

    def __init__(
        self,
        session: Session,
        embedding_provider: EmbeddingProvider,
        settings: Settings | None = None,
    ) -> None:
        self.session = session
        self.embedding_provider = embedding_provider
        self.settings = settings or get_settings()

    def ingest_bytes(
        self,
        tenant_id: str,
        filename: str,
        content: bytes,
        content_type: str | None = "text/plain",
        storage_path: str | None = None,
    ) -> KnowledgeDocument:
        """Create document metadata and store tenant-scoped chunks."""
        document = KnowledgeDocument(
            tenant_id=tenant_id,
            filename=filename,
            content_type=content_type,
            storage_path=storage_path,
            status="processing",
        )
        self.session.add(document)
        self.session.flush()

        try:
            text = extract_text(content, content_type)
            chunks = chunk_text(
                text,
                chunk_size=self.settings.rag_chunk_size,
                overlap=self.settings.rag_chunk_overlap,
            )
            if not chunks:
                raise ValueError("Document does not contain extractable text")
            embeddings = self.embedding_provider.embed_texts(chunks)
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=True)):
                self.session.add(
                    DocumentChunk(
                        tenant_id=tenant_id,
                        document_id=document.id,
                        chunk_index=index,
                        content=chunk,
                        token_count=len(chunk.split()),
                        embedding=embedding,
                    )
                )
            document.status = "ingested"
            document.error_message = None
        except Exception as exc:
            document.status = "failed"
            document.error_message = str(exc)
        finally:
            self.session.flush()

        return document
