from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import Settings
from app.db.base import Base
from app.models import DocumentChunk, KnowledgeDocument
from app.providers.ai.deterministic import DeterministicEmbeddingProvider
from app.rag.ingestion import RagIngestionService
from app.rag.retrieval import RagRetrievalService
from app.tenants.service import TenantService


def create_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True)
    return session_factory()


def create_ingestion_service(session):
    settings = Settings(
        ai_provider="test",
        ai_embedding_dimensions=16,
        rag_chunk_size=6,
        rag_chunk_overlap=2,
    )
    provider = DeterministicEmbeddingProvider(dimensions=16)
    return RagIngestionService(session, provider, settings=settings), provider


def test_ingestion_creates_tenant_scoped_document_chunks():
    with create_test_session() as session:
        tenant = TenantService(session).create_tenant("Demo Plumbing", "demo-plumbing")
        ingestion_service, _provider = create_ingestion_service(session)

        document = ingestion_service.ingest_bytes(
            tenant_id=tenant.id,
            filename="services.md",
            content=(
                b"Emergency plumbing hot water blocked drains leak detection "
                b"after hours callout"
            ),
            content_type="text/markdown",
        )
        session.commit()

        chunks = list(
            session.scalars(
                select(DocumentChunk).where(DocumentChunk.document_id == document.id)
            )
        )

        assert document.status == "ingested"
        assert document.tenant_id == tenant.id
        assert len(chunks) >= 2
        assert {chunk.tenant_id for chunk in chunks} == {tenant.id}
        assert all(chunk.embedding for chunk in chunks)


def test_ingestion_marks_document_failed_for_unsupported_content():
    with create_test_session() as session:
        tenant = TenantService(session).create_tenant("Demo Plumbing", "demo-plumbing")
        ingestion_service, _provider = create_ingestion_service(session)

        document = ingestion_service.ingest_bytes(
            tenant_id=tenant.id,
            filename="brochure.bin",
            content=b"binary",
            content_type="application/octet-stream",
        )
        session.commit()

        stored_document = session.get(KnowledgeDocument, document.id)

        assert stored_document is not None
        assert stored_document.status == "failed"
        assert "Unsupported content type" in (stored_document.error_message or "")


def test_retrieval_filters_by_tenant_before_scoring():
    with create_test_session() as session:
        tenant_service = TenantService(session)
        tenant_a = tenant_service.create_tenant("Tenant A Plumbing", "tenant-a")
        tenant_b = tenant_service.create_tenant("Tenant B Electrical", "tenant-b")
        ingestion_service, provider = create_ingestion_service(session)

        ingestion_service.ingest_bytes(
            tenant_id=tenant_a.id,
            filename="tenant-a.md",
            content=b"blocked drain emergency plumbing hot water repair",
            content_type="text/markdown",
        )
        ingestion_service.ingest_bytes(
            tenant_id=tenant_b.id,
            filename="tenant-b.md",
            content=b"blocked drain emergency plumbing hot water repair",
            content_type="text/markdown",
        )
        session.commit()

        results = RagRetrievalService(session, provider).retrieve(
            tenant_id=tenant_a.id,
            query="blocked drain emergency repair",
            limit=10,
        )

        assert results
        assert {result.chunk.tenant_id for result in results} == {tenant_a.id}
