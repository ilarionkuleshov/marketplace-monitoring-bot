from sqlalchemy.dialects.postgresql import BIGINT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class Marketplace(Base):
    """Marketplace model."""

    __tablename__ = "marketplaces"

    id: Mapped[int] = mapped_column(BIGINT(), primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(50), unique=True)
    url: Mapped[str] = mapped_column(VARCHAR(100), unique=True)
