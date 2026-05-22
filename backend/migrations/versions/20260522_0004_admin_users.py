"""Add global admin users.

Revision ID: 20260522_0004
Revises: 20260522_0003
Create Date: 2026-05-22
"""

from alembic import op
import sqlalchemy as sa


revision = "20260522_0004"
down_revision = "20260522_0003"
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
        "admin_users",
        id_column(),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        *timestamp_columns(),
        sa.UniqueConstraint("email", name="uq_admin_users_email"),
    )
    op.create_index("ix_admin_users_email", "admin_users", ["email"])
    op.create_index("ix_admin_users_role", "admin_users", ["role"])
    op.create_index("ix_admin_users_status", "admin_users", ["status"])


def downgrade() -> None:
    op.drop_table("admin_users")
