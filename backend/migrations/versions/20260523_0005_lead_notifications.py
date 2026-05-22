"""Add lead lifecycle notification schema.

Revision ID: 20260523_0005
Revises: 20260522_0004
Create Date: 2026-05-23
"""

from alembic import op
import sqlalchemy as sa


revision = "20260523_0005"
down_revision = "20260522_0004"
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
    op.add_column("leads", sa.Column("qualified_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("leads", sa.Column("qualification_reason", sa.Text(), nullable=True))
    op.add_column(
        "leads",
        sa.Column(
            "notification_status",
            sa.String(length=40),
            server_default="not_queued",
            nullable=False,
        ),
    )
    op.add_column("leads", sa.Column("last_notified_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_leads_notification_status", "leads", ["notification_status"])

    op.create_table(
        "business_notification_settings",
        id_column(),
        tenant_id_column(),
        sa.Column(
            "business_id",
            sa.String(length=36),
            sa.ForeignKey("businesses.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("notification_email", sa.String(length=255), nullable=True),
        sa.Column("lead_notifications_enabled", sa.Boolean(), nullable=False),
        *timestamp_columns(),
        sa.UniqueConstraint("tenant_id", name="uq_business_notification_settings_tenant"),
    )
    op.create_index(
        "ix_business_notification_settings_tenant_id",
        "business_notification_settings",
        ["tenant_id"],
    )
    op.create_index(
        "ix_business_notification_settings_business_id",
        "business_notification_settings",
        ["business_id"],
    )

    op.create_table(
        "notification_deliveries",
        id_column(),
        tenant_id_column(),
        sa.Column(
            "lead_id",
            sa.String(length=36),
            sa.ForeignKey("leads.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("notification_type", sa.String(length=80), nullable=False),
        sa.Column("recipient_email", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        *timestamp_columns(),
    )
    op.create_index(
        "ix_notification_deliveries_tenant_id",
        "notification_deliveries",
        ["tenant_id"],
    )
    op.create_index("ix_notification_deliveries_lead_id", "notification_deliveries", ["lead_id"])
    op.create_index("ix_notification_deliveries_status", "notification_deliveries", ["status"])
    op.create_index(
        "ix_notification_deliveries_notification_type",
        "notification_deliveries",
        ["notification_type"],
    )
    op.create_index(
        "ix_notification_deliveries_next_attempt_at",
        "notification_deliveries",
        ["next_attempt_at"],
    )


def downgrade() -> None:
    op.drop_table("notification_deliveries")
    op.drop_table("business_notification_settings")
    op.drop_index("ix_leads_notification_status", table_name="leads")
    op.drop_column("leads", "last_notified_at")
    op.drop_column("leads", "notification_status")
    op.drop_column("leads", "qualification_reason")
    op.drop_column("leads", "qualified_at")
