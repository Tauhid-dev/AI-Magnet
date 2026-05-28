"""Add tenant integrity and privacy lifecycle controls.

Revision ID: 20260528_0007
Revises: 20260528_0006
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260528_0007"
down_revision = "20260528_0006"
branch_labels = None
depends_on = None


PARENT_UNIQUE_CONSTRAINTS = (
    ("businesses", "uq_businesses_tenant_id_id", ["tenant_id", "id"]),
    (
        "knowledge_documents",
        "uq_knowledge_documents_tenant_id_id",
        ["tenant_id", "id"],
    ),
    ("conversations", "uq_conversations_tenant_id_id", ["tenant_id", "id"]),
    ("leads", "uq_leads_tenant_id_id", ["tenant_id", "id"]),
)

SAME_TENANT_FOREIGN_KEYS = (
    (
        "business_users",
        "fk_business_users_business_same_tenant",
        "businesses",
        ["tenant_id", "business_id"],
        ["tenant_id", "id"],
        None,
    ),
    (
        "document_chunks",
        "fk_document_chunks_document_same_tenant",
        "knowledge_documents",
        ["tenant_id", "document_id"],
        ["tenant_id", "id"],
        "CASCADE",
    ),
    (
        "messages",
        "fk_messages_conversation_same_tenant",
        "conversations",
        ["tenant_id", "conversation_id"],
        ["tenant_id", "id"],
        "CASCADE",
    ),
    (
        "leads",
        "fk_leads_conversation_same_tenant",
        "conversations",
        ["tenant_id", "conversation_id"],
        ["tenant_id", "id"],
        None,
    ),
    (
        "business_notification_settings",
        "fk_notification_settings_business_same_tenant",
        "businesses",
        ["tenant_id", "business_id"],
        ["tenant_id", "id"],
        None,
    ),
    (
        "notification_deliveries",
        "fk_notification_deliveries_lead_same_tenant",
        "leads",
        ["tenant_id", "lead_id"],
        ["tenant_id", "id"],
        None,
    ),
)

RELATIONSHIP_VALIDATION_QUERIES = (
    (
        "business_users.business_id",
        """
        SELECT count(*)
        FROM business_users child
        JOIN businesses parent ON parent.id = child.business_id
        WHERE child.business_id IS NOT NULL
          AND child.tenant_id != parent.tenant_id
        """,
    ),
    (
        "document_chunks.document_id",
        """
        SELECT count(*)
        FROM document_chunks child
        JOIN knowledge_documents parent ON parent.id = child.document_id
        WHERE child.tenant_id != parent.tenant_id
        """,
    ),
    (
        "messages.conversation_id",
        """
        SELECT count(*)
        FROM messages child
        JOIN conversations parent ON parent.id = child.conversation_id
        WHERE child.tenant_id != parent.tenant_id
        """,
    ),
    (
        "leads.conversation_id",
        """
        SELECT count(*)
        FROM leads child
        JOIN conversations parent ON parent.id = child.conversation_id
        WHERE child.conversation_id IS NOT NULL
          AND child.tenant_id != parent.tenant_id
        """,
    ),
    (
        "business_notification_settings.business_id",
        """
        SELECT count(*)
        FROM business_notification_settings child
        JOIN businesses parent ON parent.id = child.business_id
        WHERE child.business_id IS NOT NULL
          AND child.tenant_id != parent.tenant_id
        """,
    ),
    (
        "notification_deliveries.lead_id",
        """
        SELECT count(*)
        FROM notification_deliveries child
        JOIN leads parent ON parent.id = child.lead_id
        WHERE child.lead_id IS NOT NULL
          AND child.tenant_id != parent.tenant_id
        """,
    ),
)


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


def validate_existing_relationships() -> None:
    bind = op.get_bind()
    for relationship_name, query in RELATIONSHIP_VALIDATION_QUERIES:
        count = bind.execute(sa.text(query)).scalar_one()
        if count:
            raise RuntimeError(
                f"Cannot add tenant integrity constraints: "
                f"{relationship_name} has {count} cross-tenant rows"
            )


def upgrade() -> None:
    validate_existing_relationships()

    op.add_column("tenants", sa.Column("offboarded_at", sa.DateTime(timezone=True)))
    op.add_column("tenants", sa.Column("deletion_requested_at", sa.DateTime(timezone=True)))
    op.add_column("tenants", sa.Column("data_retention_until", sa.DateTime(timezone=True)))
    op.create_index(
        "ix_tenants_data_retention_until",
        "tenants",
        ["data_retention_until"],
    )

    op.create_table(
        "global_audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=True),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=160), nullable=False),
        sa.Column("target_type", sa.String(length=120), nullable=True),
        sa.Column("target_id", sa.String(length=36), nullable=True),
        sa.Column("attributes", sa.JSON(), nullable=True),
        *timestamp_columns(),
    )
    op.create_index("ix_global_audit_logs_tenant_id", "global_audit_logs", ["tenant_id"])
    op.create_index("ix_global_audit_logs_actor_id", "global_audit_logs", ["actor_id"])
    op.create_index("ix_global_audit_logs_action", "global_audit_logs", ["action"])

    for table_name, constraint_name, columns in PARENT_UNIQUE_CONSTRAINTS:
        with op.batch_alter_table(table_name, **batch_kwargs()) as batch_op:
            batch_op.create_unique_constraint(constraint_name, columns)

    for (
        child_table,
        constraint_name,
        parent_table,
        local_columns,
        remote_columns,
        ondelete,
    ) in SAME_TENANT_FOREIGN_KEYS:
        with op.batch_alter_table(child_table, **batch_kwargs()) as batch_op:
            batch_op.create_foreign_key(
                constraint_name,
                parent_table,
                local_columns,
                remote_columns,
                ondelete=ondelete,
            )


def downgrade() -> None:
    for (
        child_table,
        constraint_name,
        _parent_table,
        _local_columns,
        _remote_columns,
        _ondelete,
    ) in reversed(SAME_TENANT_FOREIGN_KEYS):
        with op.batch_alter_table(child_table, **batch_kwargs()) as batch_op:
            batch_op.drop_constraint(constraint_name, type_="foreignkey")

    for table_name, constraint_name, _columns in reversed(PARENT_UNIQUE_CONSTRAINTS):
        with op.batch_alter_table(table_name, **batch_kwargs()) as batch_op:
            batch_op.drop_constraint(constraint_name, type_="unique")

    op.drop_table("global_audit_logs")
    op.drop_index("ix_tenants_data_retention_until", table_name="tenants")
    op.drop_column("tenants", "data_retention_until")
    op.drop_column("tenants", "deletion_requested_at")
    op.drop_column("tenants", "offboarded_at")
