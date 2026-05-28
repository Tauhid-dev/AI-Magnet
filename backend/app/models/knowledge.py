"""Knowledge base document models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin
from app.db.vector import VectorType


class KnowledgeDocument(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Uploaded knowledge document metadata for one tenant."""

    __tablename__ = "knowledge_documents"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_knowledge_documents_tenant_id_id"),
        ForeignKeyConstraint(
            ["tenant_id", "website_source_id"],
            ["website_sources.tenant_id", "website_sources.id"],
            name="fk_knowledge_documents_website_source_same_tenant",
            ondelete="CASCADE",
        ),
    )

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False, default="manual_upload")
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    source_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    website_source_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class WebsiteSource(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Tenant-approved website or sitemap source for crawler ingestion."""

    __tablename__ = "website_sources"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_website_sources_tenant_id_id"),
        UniqueConstraint("tenant_id", "root_url", name="uq_website_sources_tenant_root_url"),
    )

    source_type: Mapped[str] = mapped_column(String(40), nullable=False)
    root_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    normalized_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="queued", index=True)
    last_job_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_pages: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    max_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_crawled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WebsiteCrawlPage(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Per-page crawl history for a tenant-owned website source."""

    __tablename__ = "website_crawl_pages"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "source_id",
            "canonical_url",
            name="uq_website_crawl_pages_tenant_source_url",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "source_id"],
            ["website_sources.tenant_id", "website_sources.id"],
            name="fk_website_crawl_pages_source_same_tenant",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "document_id"],
            ["knowledge_documents.tenant_id", "knowledge_documents.id"],
            name="fk_website_crawl_pages_document_same_tenant",
            ondelete="CASCADE",
        ),
    )

    source_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    canonical_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="queued", index=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    crawled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DocumentChunk(TenantScopedMixin, IdMixin, TimestampMixin, Base):
    """Tenant-scoped document chunk with embedding vector."""

    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_index"),
        ForeignKeyConstraint(
            ["tenant_id", "document_id"],
            ["knowledge_documents.tenant_id", "knowledge_documents.id"],
            name="fk_document_chunks_document_same_tenant",
            ondelete="CASCADE",
        ),
    )

    document_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    embedding: Mapped[list[float]] = mapped_column(VectorType(1536), nullable=False)

    document: Mapped[KnowledgeDocument] = relationship(back_populates="chunks")
