"""Update `adverts` table.

Revision ID: 9d1e9c088371
Revises: 7e43c6006b64
Create Date: 2024-12-31 18:51:17.503079

"""

# pylint: disable=C0103

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9d1e9c088371"
down_revision: str | None = "7e43c6006b64"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrades database."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("adverts", sa.Column("monitoring_run_id", sa.BigInteger(), nullable=False))
    op.add_column("adverts", sa.Column("sent_to_user", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.create_index(op.f("ix_adverts_monitoring_run_id"), "adverts", ["monitoring_run_id"], unique=False)
    op.create_foreign_key("adverts_monitoring_run_id_fkey", "adverts", "monitoring_runs", ["monitoring_run_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrades database."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("adverts_monitoring_run_id_fkey", "adverts", type_="foreignkey")
    op.drop_index(op.f("ix_adverts_monitoring_run_id"), table_name="adverts")
    op.drop_column("adverts", "sent_to_user")
    op.drop_column("adverts", "monitoring_run_id")
    # ### end Alembic commands ###