"""Updates `monitoring_run_status` enum.

Revision ID: 76e3b196066e
Revises: e8e8fd6e81ad
Create Date: 2024-11-05 19:48:06.957553

"""

# pylint: disable=C0103
# mypy: disable-error-code="attr-defined"

from typing import Sequence

from alembic import op
from alembic_postgresql_enum import TableReference

# revision identifiers, used by Alembic.
revision: str = "76e3b196066e"
down_revision: str | None = "e8e8fd6e81ad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrades database."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values(
        "public",
        "monitoring_run_status",
        ["scheduled", "queued", "running", "success", "failed"],
        [
            TableReference(
                table_schema="public",
                table_name="monitoring_runs",
                column_name="status",
                existing_server_default="'scheduled'::monitoring_run_status",
            )
        ],
        enum_values_to_rename=[],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrades database."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values(
        "public",
        "monitoring_run_status",
        ["scheduled", "running", "success", "failed"],
        [
            TableReference(
                table_schema="public",
                table_name="monitoring_runs",
                column_name="status",
                existing_server_default="'scheduled'::monitoring_run_status",
            )
        ],
        enum_values_to_rename=[],
    )
    # ### end Alembic commands ###