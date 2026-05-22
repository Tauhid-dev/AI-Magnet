"""Add document chunks vector schema.

Revision ID: 20260522_0002
Revises: 20260522_0001
Create Date: 2026-05-22
"""

from alembic import op
import sqlalchemy as sa

from app.db.vector import VectorType


revision = "20260522_0002"
down_revision = "20260522_0001"
branch_labels = None
depends_on = None


def is_postgresql() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def id_column() -> sa.Column:
    return sa.Column("id", sa.String(length=36), primary_key=True)


def timestamp_columns() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )


def upgrade() -> None:
    if is_postgresql():
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "document_chunks",
        id_column(),
        sa.Column(
            "tenant_id",
            sa.String(length=36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "document_id",
            sa.String(length=36),
            sa.ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("embedding", VectorType(1536), nullable=False),
        *timestamp_columns(),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_index"),
    )
    op.create_index("ix_document_chunks_tenant_id", "document_chunks", ["tenant_id"])
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])

    if is_postgresql():
        op.execute(
            "CREATE INDEX ix_document_chunks_embedding_cosine "
            "ON document_chunks USING ivfflat (embedding vector_cosine_ops)"
        )


def downgrade() -> None:
    op.drop_table("document_chunks")
