"""Creates `monitoring_runs` table.

Revision ID: caa3c3c8869a
Revises: 78262223d113
Create Date: 2024-09-29 19:49:57.971307

"""

# pylint: disable=R0801

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "caa3c3c8869a"
down_revision: str | None = "78262223d113"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrades database."""
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum("scheduled", "running", "success", "failed", name="monitoring_run_status").create(op.get_bind())
    op.create_table(
        "monitoring_runs",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("monitoring_id", sa.BigInteger(), nullable=False),
        sa.Column("log_file", sa.String(length=200), nullable=True),
        sa.Column("duration", sa.Interval(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "scheduled", "running", "success", "failed", name="monitoring_run_status", create_type=False
            ),
            server_default=sa.text("'scheduled'"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["monitoring_id"],
            ["monitorings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_monitoring_runs_created_at"), "monitoring_runs", ["created_at"], unique=False)
    op.create_index(op.f("ix_monitoring_runs_duration"), "monitoring_runs", ["duration"], unique=False)
    op.create_index(op.f("ix_monitoring_runs_monitoring_id"), "monitoring_runs", ["monitoring_id"], unique=False)
    op.create_index(op.f("ix_monitoring_runs_status"), "monitoring_runs", ["status"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrades database."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_monitoring_runs_status"), table_name="monitoring_runs")
    op.drop_index(op.f("ix_monitoring_runs_monitoring_id"), table_name="monitoring_runs")
    op.drop_index(op.f("ix_monitoring_runs_duration"), table_name="monitoring_runs")
    op.drop_index(op.f("ix_monitoring_runs_created_at"), table_name="monitoring_runs")
    op.drop_table("monitoring_runs")
    sa.Enum("scheduled", "running", "success", "failed", name="monitoring_run_status").drop(op.get_bind())
    # ### end Alembic commands ###
