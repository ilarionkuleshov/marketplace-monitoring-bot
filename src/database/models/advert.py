from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import BIGINT, FLOAT, TIMESTAMP, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import BaseModel


class Advert(BaseModel):
    """Advert model."""

    __tablename__ = "adverts"

    id: Mapped[int] = mapped_column(BIGINT(), primary_key=True)
    monitoring_id: Mapped[int] = mapped_column(BIGINT(), ForeignKey("monitorings.id"))
    external_id: Mapped[str] = mapped_column(VARCHAR(100))
    url: Mapped[str] = mapped_column(VARCHAR(1000))
    image: Mapped[str] = mapped_column(VARCHAR(1000), nullable=True)
    title: Mapped[str] = mapped_column(VARCHAR(100))
    description: Mapped[str] = mapped_column(VARCHAR(200), nullable=True)
    price: Mapped[float] = mapped_column(FLOAT(), nullable=True)
    max_price: Mapped[float] = mapped_column(FLOAT(), nullable=True)
    currency: Mapped[str] = mapped_column(VARCHAR(3))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), index=True, server_default=text("now()"))

    __table_args__ = (UniqueConstraint("monitoring_id", "external_id"),)
