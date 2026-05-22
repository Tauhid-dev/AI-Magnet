"""Initial tenant schema.

Revision ID: 20260522_0001
Revises:
Create Date: 2026-05-22
"""

from alembic import op
import sqlalchemy as sa


revision = "20260522_0001"
down_revision = None
branch_labels = None
depends_on = None


def id_column() -> sa.Column:
    return sa.Column("id", sa.String(length=36), primary_key=True)


def tenant_id_column() -> sa.Column:
    return sa.Column(
        "tenant_id",
        sa.String(length=36),
        sa.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )


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
        "tenants",
        id_column(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        *timestamp_columns(),
        sa.UniqueConstraint("slug", name="uq_tenants_slug"),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"])
    op.create_index("ix_tenants_status", "tenants", ["status"])

    op.create_table(
        "businesses",
        id_column(),
        tenant_id_column(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=80), nullable=True),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        *timestamp_columns(),
        sa.UniqueConstraint("tenant_id", "name", name="uq_business_tenant_name"),
    )
    op.create_index("ix_businesses_tenant_id", "businesses", ["tenant_id"])

    op.create_table(
        "business_users",
        id_column(),
        tenant_id_column(),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column(
            "business_id",
            sa.String(length=36),
            sa.ForeignKey("businesses.id", ondelete="SET NULL"),
            nullable=True,
        ),
        *timestamp_columns(),
        sa.UniqueConstraint("tenant_id", "email", name="uq_business_user_tenant_email"),
    )
    op.create_index("ix_business_users_tenant_id", "business_users", ["tenant_id"])
    op.create_index("ix_business_users_business_id", "business_users", ["business_id"])

    op.create_table(
        "knowledge_documents",
        id_column(),
        tenant_id_column(),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("storage_path", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        *timestamp_columns(),
    )
    op.create_index("ix_knowledge_documents_tenant_id", "knowledge_documents", ["tenant_id"])

    op.create_table(
        "conversations",
        id_column(),
        tenant_id_column(),
        sa.Column("visitor_label", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        *timestamp_columns(),
    )
    op.create_index("ix_conversations_tenant_id", "conversations", ["tenant_id"])
    op.create_index("ix_conversations_status", "conversations", ["status"])

    op.create_table(
        "messages",
        id_column(),
        tenant_id_column(),
        sa.Column(
            "conversation_id",
            sa.String(length=36),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sender_type", sa.String(length=40), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        *timestamp_columns(),
    )
    op.create_index("ix_messages_tenant_id", "messages", ["tenant_id"])
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    op.create_table(
        "leads",
        id_column(),
        tenant_id_column(),
        sa.Column(
            "conversation_id",
            sa.String(length=36),
            sa.ForeignKey("conversations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("customer_email", sa.String(length=255), nullable=True),
        sa.Column("customer_phone", sa.String(length=80), nullable=True),
        sa.Column("job_type", sa.String(length=160), nullable=True),
        sa.Column("suburb", sa.String(length=160), nullable=True),
        sa.Column("urgency", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
    )
    op.create_index("ix_leads_tenant_id", "leads", ["tenant_id"])
    op.create_index("ix_leads_conversation_id", "leads", ["conversation_id"])
    op.create_index("ix_leads_status", "leads", ["status"])

    op.create_table(
        "usage_logs",
        id_column(),
        tenant_id_column(),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("event_source", sa.String(length=120), nullable=True),
        sa.Column("attributes", sa.JSON(), nullable=True),
        *timestamp_columns(),
    )
    op.create_index("ix_usage_logs_tenant_id", "usage_logs", ["tenant_id"])
    op.create_index("ix_usage_logs_event_type", "usage_logs", ["event_type"])

    op.create_table(
        "audit_logs",
        id_column(),
        tenant_id_column(),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=160), nullable=False),
        sa.Column("target_type", sa.String(length=120), nullable=True),
        sa.Column("target_id", sa.String(length=36), nullable=True),
        sa.Column("attributes", sa.JSON(), nullable=True),
        *timestamp_columns(),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("usage_logs")
    op.drop_table("leads")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("knowledge_documents")
    op.drop_table("business_users")
    op.drop_table("businesses")
    op.drop_table("tenants")
