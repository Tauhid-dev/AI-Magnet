"""Add password auth and session security fields.

Revision ID: 20260528_0006
Revises: 20260523_0005
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260528_0006"
down_revision = "20260523_0005"
branch_labels = None
depends_on = None


def auth_columns(include_mfa: bool = False) -> list[sa.Column]:
    columns = [
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("password_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("session_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("failed_login_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    ]
    if include_mfa:
        columns.extend(
            [
                sa.Column("mfa_required", sa.Boolean(), server_default=sa.true(), nullable=False),
                sa.Column("mfa_secret", sa.String(length=255), nullable=True),
            ]
        )
    return columns


def upgrade() -> None:
    for column in auth_columns():
        op.add_column("business_users", column)
    op.create_index("ix_business_users_locked_until", "business_users", ["locked_until"])

    for column in auth_columns(include_mfa=True):
        op.add_column("admin_users", column)
    op.create_index("ix_admin_users_locked_until", "admin_users", ["locked_until"])


def downgrade() -> None:
    op.drop_index("ix_admin_users_locked_until", table_name="admin_users")
    op.drop_column("admin_users", "mfa_secret")
    op.drop_column("admin_users", "mfa_required")
    op.drop_column("admin_users", "last_login_at")
    op.drop_column("admin_users", "locked_until")
    op.drop_column("admin_users", "failed_login_count")
    op.drop_column("admin_users", "session_version")
    op.drop_column("admin_users", "password_updated_at")
    op.drop_column("admin_users", "password_hash")

    op.drop_index("ix_business_users_locked_until", table_name="business_users")
    op.drop_column("business_users", "last_login_at")
    op.drop_column("business_users", "locked_until")
    op.drop_column("business_users", "failed_login_count")
    op.drop_column("business_users", "session_version")
    op.drop_column("business_users", "password_updated_at")
    op.drop_column("business_users", "password_hash")
