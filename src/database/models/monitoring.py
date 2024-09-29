from datetime import datetime, timedelta

from sqlalchemy import text, BigInteger, DateTime, String, Interval, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import DatabaseModel


class Monitoring(DatabaseModel):
    """Monitoring model."""

    __tablename__ = "monitorings"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger(), ForeignKey("users.id"), index=True)
    marketplace_id: Mapped[int] = mapped_column(BigInteger(), ForeignKey("marketplaces.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(2000))
    run_interval: Mapped[timedelta] = mapped_column(Interval(), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean(), default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, server_default=text("now()"))

    __table_args__ = (UniqueConstraint("user_id", "url"),)
