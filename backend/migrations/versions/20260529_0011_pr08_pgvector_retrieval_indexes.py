"""Add pgvector retrieval indexes for tenant-scoped RAG search.

Revision ID: 20260529_0011
Revises: 20260529_0010
Create Date: 2026-05-29
"""

from alembic import op


revision = "20260529_0011"
down_revision = "20260529_0010"
branch_labels = None
depends_on = None


def is_postgresql() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def upgrade() -> None:
    if not is_postgresql():
        return
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw_cosine
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_document_chunks_tenant_document
        ON document_chunks (tenant_id, document_id)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_knowledge_documents_tenant_status
        ON knowledge_documents (tenant_id, status)
        """
    )


def downgrade() -> None:
    if not is_postgresql():
        return
    op.execute("DROP INDEX IF EXISTS ix_knowledge_documents_tenant_status")
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_tenant_document")
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw_cosine")
