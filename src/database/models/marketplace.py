from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import BaseModel


class Marketplace(BaseModel):
    """Marketplace model."""

    __tablename__ = "marketplaces"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    url: Mapped[str] = mapped_column(String(200), unique=True)
