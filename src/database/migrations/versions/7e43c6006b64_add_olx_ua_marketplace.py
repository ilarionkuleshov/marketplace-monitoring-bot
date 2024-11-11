"""Adds `olx.ua` marketplace.

Revision ID: 7e43c6006b64
Revises: 76e3b196066e
Create Date: 2024-11-07 20:42:01.600451

"""

# pylint: disable=C0103

from typing import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7e43c6006b64"
down_revision: str | None = "76e3b196066e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrades database."""
    op.execute("insert into marketplaces (name, url) values ('Olx UA', 'https://olx.ua/')")


def downgrade() -> None:
    """Downgrades database."""
    op.execute("delete from marketplaces where name = 'Olx UA'")
