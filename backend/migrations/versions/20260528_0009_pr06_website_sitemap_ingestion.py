"""Add website and sitemap ingestion tracking.

Revision ID: 20260528_0009
Revises: 20260528_0008
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260528_0009"
down_revision = "20260528_0008"
branch_labels = None
depends_on = None


def batch_kwargs() -> dict[str, str]:
    if op.get_bind().dialect.name == "sqlite":
        return {"recreate": "always"}
    return {}


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
    op.create_table(
        "website_sources",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("root_url", sa.String(length=2000), nullable=False),
        sa.Column("normalized_domain", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="queued"),
        sa.Column("last_job_id", sa.String(length=36), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("max_pages", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("max_depth", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_crawled_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_website_sources_tenant_id_id"),
        sa.UniqueConstraint("tenant_id", "root_url", name="uq_website_sources_tenant_root_url"),
    )
    op.create_index("ix_website_sources_tenant_id", "website_sources", ["tenant_id"])
    op.create_index(
        "ix_website_sources_normalized_domain",
        "website_sources",
        ["normalized_domain"],
    )
    op.create_index("ix_website_sources_status", "website_sources", ["status"])
    op.create_index("ix_website_sources_last_job_id", "website_sources", ["last_job_id"])

    with op.batch_alter_table("knowledge_documents", **batch_kwargs()) as batch_op:
        batch_op.add_column(
            sa.Column(
                "source_type",
                sa.String(length=60),
                nullable=False,
                server_default="manual_upload",
            )
        )
        batch_op.add_column(sa.Column("source_url", sa.String(length=2000), nullable=True))
        batch_op.add_column(sa.Column("source_title", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("source_hash", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("website_source_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            "fk_knowledge_documents_website_source_same_tenant",
            "website_sources",
            ["tenant_id", "website_source_id"],
            ["tenant_id", "id"],
            ondelete="CASCADE",
        )
    op.create_index(
        "ix_knowledge_documents_website_source_id",
        "knowledge_documents",
        ["website_source_id"],
    )

    op.create_table(
        "website_crawl_pages",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("url", sa.String(length=2000), nullable=False),
        sa.Column("canonical_url", sa.String(length=2000), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="queued"),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("crawled_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "source_id"],
            ["website_sources.tenant_id", "website_sources.id"],
            name="fk_website_crawl_pages_source_same_tenant",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "document_id"],
            ["knowledge_documents.tenant_id", "knowledge_documents.id"],
            name="fk_website_crawl_pages_document_same_tenant",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "source_id",
            "canonical_url",
            name="uq_website_crawl_pages_tenant_source_url",
        ),
    )
    op.create_index("ix_website_crawl_pages_tenant_id", "website_crawl_pages", ["tenant_id"])
    op.create_index("ix_website_crawl_pages_source_id", "website_crawl_pages", ["source_id"])
    op.create_index("ix_website_crawl_pages_status", "website_crawl_pages", ["status"])
    op.create_index(
        "ix_website_crawl_pages_document_id",
        "website_crawl_pages",
        ["document_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_website_crawl_pages_document_id", table_name="website_crawl_pages")
    op.drop_index("ix_website_crawl_pages_status", table_name="website_crawl_pages")
    op.drop_index("ix_website_crawl_pages_source_id", table_name="website_crawl_pages")
    op.drop_index("ix_website_crawl_pages_tenant_id", table_name="website_crawl_pages")
    op.drop_table("website_crawl_pages")

    op.drop_index(
        "ix_knowledge_documents_website_source_id",
        table_name="knowledge_documents",
    )
    with op.batch_alter_table("knowledge_documents", **batch_kwargs()) as batch_op:
        batch_op.drop_constraint(
            "fk_knowledge_documents_website_source_same_tenant",
            type_="foreignkey",
        )
        batch_op.drop_column("website_source_id")
        batch_op.drop_column("source_hash")
        batch_op.drop_column("source_title")
        batch_op.drop_column("source_url")
        batch_op.drop_column("source_type")

    op.drop_index("ix_website_sources_last_job_id", table_name="website_sources")
    op.drop_index("ix_website_sources_status", table_name="website_sources")
    op.drop_index("ix_website_sources_normalized_domain", table_name="website_sources")
    op.drop_index("ix_website_sources_tenant_id", table_name="website_sources")
    op.drop_table("website_sources")
