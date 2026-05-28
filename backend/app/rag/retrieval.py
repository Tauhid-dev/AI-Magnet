"""Tenant-scoped RAG retrieval service."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select, text
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings, get_settings
from app.models.knowledge import DocumentChunk, KnowledgeDocument
from app.providers.ai.base import EmbeddingProvider
from app.rag.scoring import cosine_similarity


@dataclass(frozen=True)
class RetrievalCitation:
    """Source citation metadata safe to expose through chat responses."""

    citation_id: str
    document_id: str
    chunk_id: str
    chunk_index: int
    score: float
    filename: str
    source_type: str
    source_title: str | None = None
    source_url: str | None = None


@dataclass(frozen=True)
class RetrievalResult:
    """Retrieved chunk and similarity score."""

    chunk: DocumentChunk
    score: float
    citation: RetrievalCitation


class RagRetrievalService:
    """Retrieve relevant chunks with tenant filtering inside the retrieval query."""

    def __init__(
        self,
        session: Session,
        embedding_provider: EmbeddingProvider,
        settings: Settings | None = None,
    ) -> None:
        self.session = session
        self.embedding_provider = embedding_provider
        self.settings = settings or get_settings()

    def retrieve(
        self,
        tenant_id: str,
        query: str,
        limit: int = 5,
        min_score: float | None = None,
    ) -> list[RetrievalResult]:
        """Return bounded top tenant-owned chunks for a query."""
        top_k = max(1, min(limit, 20))
        threshold = self.settings.rag_similarity_threshold if min_score is None else min_score
        query_embedding = self.embedding_provider.embed_texts([query])[0]
        if self._supports_pgvector_sql():
            return self._retrieve_with_pgvector_sql(
                tenant_id=tenant_id,
                query_embedding=query_embedding,
                limit=top_k,
                min_score=threshold,
            )
        return self._retrieve_with_python_scoring(
            tenant_id=tenant_id,
            query_embedding=query_embedding,
            limit=top_k,
            min_score=threshold,
        )

    def _supports_pgvector_sql(self) -> bool:
        """Return true when database-side pgvector scoring is available."""
        return self.session.get_bind().dialect.name == "postgresql"

    def _retrieve_with_pgvector_sql(
        self,
        *,
        tenant_id: str,
        query_embedding: list[float],
        limit: int,
        min_score: float,
    ) -> list[RetrievalResult]:
        """Use PostgreSQL/pgvector cosine distance with tenant filter in SQL."""
        vector_literal = vector_literal_for_pgvector(query_embedding)
        retrieval_sql = text(
            """
            SELECT
                dc.id AS chunk_id,
                1 - (dc.embedding <=> CAST(:query_embedding AS vector)) AS score
            FROM document_chunks dc
            JOIN knowledge_documents kd
              ON kd.tenant_id = dc.tenant_id
             AND kd.id = dc.document_id
            WHERE dc.tenant_id = :tenant_id
              AND kd.tenant_id = :tenant_id
              AND kd.status = 'ingested'
              AND (1 - (dc.embedding <=> CAST(:query_embedding AS vector))) >= :min_score
            ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :limit
            """
        )
        rows = list(
            self.session.execute(
                retrieval_sql,
                {
                    "tenant_id": tenant_id,
                    "query_embedding": vector_literal,
                    "min_score": min_score,
                    "limit": limit,
                },
            ).mappings()
        )
        chunk_ids = [str(row["chunk_id"]) for row in rows]
        scores = {str(row["chunk_id"]): float(row["score"] or 0.0) for row in rows}
        chunks = self._load_chunks_by_id(tenant_id, chunk_ids)
        return [
            self._result_for_chunk(
                chunk=chunks[chunk_id],
                score=scores[chunk_id],
                citation_index=index,
            )
            for index, chunk_id in enumerate(chunk_ids, start=1)
            if chunk_id in chunks
        ]

    def _retrieve_with_python_scoring(
        self,
        *,
        tenant_id: str,
        query_embedding: list[float],
        limit: int,
        min_score: float,
    ) -> list[RetrievalResult]:
        """SQLite/test fallback that keeps the same tenant and status filters."""
        statement = (
            select(DocumentChunk)
            .join(
                KnowledgeDocument,
                (KnowledgeDocument.tenant_id == DocumentChunk.tenant_id)
                & (KnowledgeDocument.id == DocumentChunk.document_id),
            )
            .options(selectinload(DocumentChunk.document))
            .where(
                DocumentChunk.tenant_id == tenant_id,
                KnowledgeDocument.status == "ingested",
            )
        )
        tenant_chunks = list(self.session.scalars(statement))
        scored: list[tuple[DocumentChunk, float]] = [
            (chunk, cosine_similarity(query_embedding, chunk.embedding))
            for chunk in tenant_chunks
        ]
        scored = [result for result in scored if result[1] >= min_score]
        scored.sort(key=lambda result: result[1], reverse=True)
        return [
            self._result_for_chunk(
                chunk=chunk,
                score=score,
                citation_index=index,
            )
            for index, (chunk, score) in enumerate(scored[:limit], start=1)
        ]

    def _load_chunks_by_id(
        self,
        tenant_id: str,
        chunk_ids: list[str],
    ) -> dict[str, DocumentChunk]:
        if not chunk_ids:
            return {}
        statement = (
            select(DocumentChunk)
            .options(selectinload(DocumentChunk.document))
            .where(DocumentChunk.tenant_id == tenant_id, DocumentChunk.id.in_(chunk_ids))
        )
        return {chunk.id: chunk for chunk in self.session.scalars(statement)}

    def _result_for_chunk(
        self,
        *,
        chunk: DocumentChunk,
        score: float,
        citation_index: int,
    ) -> RetrievalResult:
        return RetrievalResult(
            chunk=chunk,
            score=score,
            citation=self._citation_for_chunk(
                chunk=chunk,
                score=score,
                citation_index=citation_index,
            ),
        )

    def _citation_for_chunk(
        self,
        *,
        chunk: DocumentChunk,
        score: float,
        citation_index: int,
    ) -> RetrievalCitation:
        document = chunk.document
        return RetrievalCitation(
            citation_id=f"S{citation_index}",
            document_id=document.id,
            chunk_id=chunk.id,
            chunk_index=chunk.chunk_index,
            score=round(score, 6),
            filename=document.filename,
            source_type=document.source_type,
            source_title=document.source_title,
            source_url=document.source_url,
        )


def vector_literal_for_pgvector(vector: list[float]) -> str:
    """Format a pgvector literal for a bound SQL parameter."""
    return "[" + ",".join(format(value, ".9g") for value in vector) + "]"
