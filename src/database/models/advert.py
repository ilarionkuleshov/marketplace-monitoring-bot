from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import DatabaseModel


class Advert(DatabaseModel):
    """Advert model."""

    __tablename__ = "adverts"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    monitoring_id: Mapped[int] = mapped_column(BigInteger(), ForeignKey("monitorings.id"), index=True)
    monitoring_run_id: Mapped[int] = mapped_column(BigInteger(), ForeignKey("monitoring_runs.id"), index=True)
    url: Mapped[str] = mapped_column(String(2000))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    image: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    price: Mapped[float | None] = mapped_column(Float(), nullable=True)
    max_price: Mapped[float | None] = mapped_column(Float(), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    sent_to_user: Mapped[bool] = mapped_column(Boolean(), default=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, server_default=text("now()"))

    __table_args__ = (UniqueConstraint("monitoring_id", "url"),)
