"""Add widget configuration schema.

Revision ID: 20260522_0003
Revises: 20260522_0002
Create Date: 2026-05-22
"""

from alembic import op
import sqlalchemy as sa


revision = "20260522_0003"
down_revision = "20260522_0002"
branch_labels = None
depends_on = None


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
    op.create_table(
        "widget_configs",
        id_column(),
        sa.Column(
            "tenant_id",
            sa.String(length=36),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("widget_key_hash", sa.String(length=128), nullable=False),
        sa.Column("key_prefix", sa.String(length=24), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("allowed_origins", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.UniqueConstraint("widget_key_hash", name="uq_widget_configs_key_hash"),
    )
    op.create_index("ix_widget_configs_tenant_id", "widget_configs", ["tenant_id"])
    op.create_index("ix_widget_configs_widget_key_hash", "widget_configs", ["widget_key_hash"])
    op.create_index("ix_widget_configs_key_prefix", "widget_configs", ["key_prefix"])
    op.create_index("ix_widget_configs_status", "widget_configs", ["status"])


def downgrade() -> None:
    op.drop_table("widget_configs")
