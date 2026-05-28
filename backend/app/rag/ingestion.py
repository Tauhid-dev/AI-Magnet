"""Tenant-scoped RAG ingestion service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.knowledge import DocumentChunk, KnowledgeDocument
from app.providers.ai.base import EmbeddingProvider
from app.rag.chunking import chunk_text
from app.rag.extraction import OcrRequiredError, extract_text


class RagIngestionService:
    """Ingest tenant knowledge documents into chunks and embeddings."""

    def __init__(
        self,
        session: Session,
        embedding_provider: EmbeddingProvider | None,
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
        document = self.create_pending_document(
            tenant_id=tenant_id,
            filename=filename,
            content_type=content_type,
            storage_path=storage_path,
            status="processing",
        )
        return self.process_document_bytes(
            document=document,
            content=content,
            content_type=content_type,
        )

    def create_pending_document(
        self,
        tenant_id: str,
        filename: str,
        content_type: str | None = "text/plain",
        storage_path: str | None = None,
        source_type: str = "manual_upload",
        source_title: str | None = None,
        source_hash: str | None = None,
        file_size_bytes: int | None = None,
        file_sha256: str | None = None,
        malware_scan_status: str = "not_scanned",
        status: str = "queued",
    ) -> KnowledgeDocument:
        """Create tenant document metadata before async processing."""
        document = KnowledgeDocument(
            tenant_id=tenant_id,
            filename=filename,
            content_type=content_type,
            storage_path=storage_path,
            source_type=source_type,
            source_title=source_title,
            source_hash=source_hash,
            file_size_bytes=file_size_bytes,
            file_sha256=file_sha256,
            malware_scan_status=malware_scan_status,
            extraction_status="pending",
            ocr_status="not_required",
            status=status,
        )
        self.session.add(document)
        self.session.flush()
        return document

    def process_document_bytes(
        self,
        document: KnowledgeDocument,
        content: bytes,
        content_type: str | None = "text/plain",
        *,
        raise_on_failure: bool = False,
    ) -> KnowledgeDocument:
        """Process content for an existing tenant document row."""
        document.status = "processing"
        document.extraction_status = "processing"
        document.ocr_status = "not_required"
        document.error_message = None
        for chunk in list(document.chunks):
            self.session.delete(chunk)
        self.session.flush()
        try:
            text = extract_text(
                content,
                content_type,
                max_pages=self.settings.document_upload_max_pages,
                ocr_enabled=self.settings.document_ocr_enabled,
            )
            chunks = chunk_text(
                text,
                chunk_size=self.settings.rag_chunk_size,
                overlap=self.settings.rag_chunk_overlap,
            )
            if not chunks:
                raise ValueError("Document does not contain extractable text")
            if self.embedding_provider is None:
                raise RuntimeError("Embedding provider is required to process documents")
            embeddings = self.embedding_provider.embed_texts(chunks)
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=True)):
                self.session.add(
                    DocumentChunk(
                        tenant_id=document.tenant_id,
                        document_id=document.id,
                        chunk_index=index,
                        content=chunk,
                        token_count=len(chunk.split()),
                        embedding=embedding,
                    )
                )
            document.status = "ingested"
            document.extraction_status = "extracted"
            document.error_message = None
        except OcrRequiredError as exc:
            document.status = "failed"
            document.extraction_status = "failed"
            document.ocr_status = "required"
            document.error_message = str(exc)
            if raise_on_failure:
                raise
        except Exception as exc:
            document.status = "failed"
            document.extraction_status = "failed"
            document.error_message = str(exc)
            if raise_on_failure:
                raise
        finally:
            self.session.flush()

        return document
