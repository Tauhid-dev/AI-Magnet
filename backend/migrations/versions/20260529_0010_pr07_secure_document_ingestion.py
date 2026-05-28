"""Add secure document ingestion metadata.

Revision ID: 20260529_0010
Revises: 20260528_0009
Create Date: 2026-05-29
"""

from alembic import op
import sqlalchemy as sa


revision = "20260529_0010"
down_revision = "20260528_0009"
branch_labels = None
depends_on = None


def batch_kwargs() -> dict[str, str]:
    if op.get_bind().dialect.name == "sqlite":
        return {"recreate": "always"}
    return {}


def upgrade() -> None:
    with op.batch_alter_table("knowledge_documents", **batch_kwargs()) as batch_op:
        batch_op.add_column(sa.Column("file_size_bytes", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("file_sha256", sa.String(length=64), nullable=True))
        batch_op.add_column(
            sa.Column(
                "malware_scan_status",
                sa.String(length=40),
                nullable=False,
                server_default="not_scanned",
            )
        )
        batch_op.add_column(
            sa.Column(
                "extraction_status",
                sa.String(length=40),
                nullable=False,
                server_default="pending",
            )
        )
        batch_op.add_column(
            sa.Column(
                "ocr_status",
                sa.String(length=40),
                nullable=False,
                server_default="not_required",
            )
        )
    op.create_index(
        "ix_knowledge_documents_file_sha256",
        "knowledge_documents",
        ["file_sha256"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_documents_file_sha256", table_name="knowledge_documents")
    with op.batch_alter_table("knowledge_documents", **batch_kwargs()) as batch_op:
        batch_op.drop_column("ocr_status")
        batch_op.drop_column("extraction_status")
        batch_op.drop_column("malware_scan_status")
        batch_op.drop_column("file_sha256")
        batch_op.drop_column("file_size_bytes")
