"""Tenant-scoped RAG retrieval service."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge import DocumentChunk
from app.providers.ai.base import EmbeddingProvider
from app.rag.scoring import cosine_similarity


@dataclass(frozen=True)
class RetrievalResult:
    """Retrieved chunk and similarity score."""

    chunk: DocumentChunk
    score: float


class RagRetrievalService:
    """Retrieve relevant chunks while filtering by tenant first."""

    def __init__(
        self,
        session: Session,
        embedding_provider: EmbeddingProvider,
    ) -> None:
        self.session = session
        self.embedding_provider = embedding_provider

    def retrieve(
        self,
        tenant_id: str,
        query: str,
        limit: int = 5,
    ) -> list[RetrievalResult]:
        """Return top tenant-owned chunks for a query."""
        query_embedding = self.embedding_provider.embed_texts([query])[0]
        statement = select(DocumentChunk).where(DocumentChunk.tenant_id == tenant_id)
        tenant_chunks = list(self.session.scalars(statement))
        scored = [
            RetrievalResult(
                chunk=chunk,
                score=cosine_similarity(query_embedding, chunk.embedding),
            )
            for chunk in tenant_chunks
        ]
        scored.sort(key=lambda result: result.score, reverse=True)
        return scored[:limit]
