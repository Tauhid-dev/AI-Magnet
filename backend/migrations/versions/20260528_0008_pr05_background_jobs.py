"""Add durable background jobs and worker heartbeats.

Revision ID: 20260528_0008
Revises: 20260528_0007
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260528_0008"
down_revision = "20260528_0007"
branch_labels = None
depends_on = None


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
        "background_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=True),
        sa.Column("queue_name", sa.String(length=80), nullable=False, server_default="default"),
        sa.Column("job_type", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="queued"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=255), nullable=True),
        sa.Column("sensitive_payload", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_by", sa.String(length=120), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("idempotency_key", name="uq_background_jobs_idempotency_key"),
    )
    op.create_index("ix_background_jobs_tenant_id", "background_jobs", ["tenant_id"])
    op.create_index("ix_background_jobs_queue_name", "background_jobs", ["queue_name"])
    op.create_index("ix_background_jobs_job_type", "background_jobs", ["job_type"])
    op.create_index("ix_background_jobs_status", "background_jobs", ["status"])
    op.create_index("ix_background_jobs_scheduled_at", "background_jobs", ["scheduled_at"])
    op.create_index("ix_background_jobs_locked_by", "background_jobs", ["locked_by"])
    op.create_index(
        "ix_background_jobs_idempotency_key",
        "background_jobs",
        ["idempotency_key"],
    )

    op.create_table(
        "worker_heartbeats",
        sa.Column("worker_id", sa.String(length=120), primary_key=True),
        sa.Column("queue_name", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="starting"),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.Column("pid", sa.Integer(), nullable=True),
        sa.Column("current_job_id", sa.String(length=36), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("stopping_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
    )
    op.create_index("ix_worker_heartbeats_queue_name", "worker_heartbeats", ["queue_name"])
    op.create_index("ix_worker_heartbeats_status", "worker_heartbeats", ["status"])
    op.create_index(
        "ix_worker_heartbeats_current_job_id",
        "worker_heartbeats",
        ["current_job_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_worker_heartbeats_current_job_id", table_name="worker_heartbeats")
    op.drop_index("ix_worker_heartbeats_status", table_name="worker_heartbeats")
    op.drop_index("ix_worker_heartbeats_queue_name", table_name="worker_heartbeats")
    op.drop_table("worker_heartbeats")

    op.drop_index("ix_background_jobs_idempotency_key", table_name="background_jobs")
    op.drop_index("ix_background_jobs_locked_by", table_name="background_jobs")
    op.drop_index("ix_background_jobs_scheduled_at", table_name="background_jobs")
    op.drop_index("ix_background_jobs_status", table_name="background_jobs")
    op.drop_index("ix_background_jobs_job_type", table_name="background_jobs")
    op.drop_index("ix_background_jobs_queue_name", table_name="background_jobs")
    op.drop_index("ix_background_jobs_tenant_id", table_name="background_jobs")
    op.drop_table("background_jobs")
