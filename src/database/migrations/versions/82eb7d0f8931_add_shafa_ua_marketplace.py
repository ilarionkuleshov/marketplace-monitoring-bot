"""Adds `shafa.ua` marketplace.

Revision ID: 82eb7d0f8931
Revises: a56adf4ac6a3
Create Date: 2025-03-09 12:06:56.694280

"""

# pylint: disable=C0103

from typing import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "82eb7d0f8931"
down_revision: str | None = "a56adf4ac6a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrades database."""
    op.execute("insert into marketplaces (name, url) values ('Shafa UA', 'https://shafa.ua/')")


def downgrade() -> None:
    """Downgrades database."""
    op.execute("delete from marketplaces where name = 'Shafa UA'")
