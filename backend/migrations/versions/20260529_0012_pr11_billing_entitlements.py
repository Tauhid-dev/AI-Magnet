"""Add tenant billing entitlements for manual paid beta.

Revision ID: 20260529_0012
Revises: 20260529_0011
Create Date: 2026-05-29
"""

from alembic import op
import sqlalchemy as sa


revision = "20260529_0012"
down_revision = "20260529_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_subscriptions",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("plan_code", sa.String(length=80), nullable=False),
        sa.Column("plan_name", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("billing_mode", sa.String(length=40), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("monthly_price_cents", sa.Integer(), nullable=False),
        sa.Column("support_level", sa.String(length=80), nullable=False),
        sa.Column("chat_conversations_limit", sa.Integer(), nullable=False),
        sa.Column("ai_responses_limit", sa.Integer(), nullable=False),
        sa.Column("tokens_limit", sa.Integer(), nullable=False),
        sa.Column("monthly_budget_cents", sa.Float(), nullable=False),
        sa.Column("documents_limit", sa.Integer(), nullable=False),
        sa.Column("storage_mb_limit", sa.Integer(), nullable=False),
        sa.Column("pages_crawled_limit", sa.Integer(), nullable=False),
        sa.Column("trial_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("billing_contact_email", sa.String(length=255), nullable=True),
        sa.Column("manual_reference", sa.String(length=160), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("updated_by_admin_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", name="uq_tenant_subscriptions_tenant_id"),
    )
    op.create_index(
        "ix_tenant_subscriptions_tenant_id",
        "tenant_subscriptions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_tenant_subscriptions_plan_code",
        "tenant_subscriptions",
        ["plan_code"],
    )
    op.create_index(
        "ix_tenant_subscriptions_status",
        "tenant_subscriptions",
        ["status"],
    )
    op.create_index(
        "ix_tenant_subscriptions_updated_by_admin_id",
        "tenant_subscriptions",
        ["updated_by_admin_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_tenant_subscriptions_updated_by_admin_id", table_name="tenant_subscriptions")
    op.drop_index("ix_tenant_subscriptions_status", table_name="tenant_subscriptions")
    op.drop_index("ix_tenant_subscriptions_plan_code", table_name="tenant_subscriptions")
    op.drop_index("ix_tenant_subscriptions_tenant_id", table_name="tenant_subscriptions")
    op.drop_table("tenant_subscriptions")
