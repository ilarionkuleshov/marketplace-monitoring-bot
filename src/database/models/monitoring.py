from datetime import datetime, timedelta

from sqlalchemy import ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import BIGINT, BOOLEAN, INTERVAL, TIMESTAMP, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import BaseModel


class Monitoring(BaseModel):
    """Monitoring model."""

    __tablename__ = "monitorings"

    id: Mapped[int] = mapped_column(BIGINT(), primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT(), ForeignKey("users.id"))
    marketplace_id: Mapped[int] = mapped_column(BIGINT(), ForeignKey("marketplaces.id"))
    name: Mapped[str] = mapped_column(VARCHAR(50))
    url: Mapped[str] = mapped_column(VARCHAR(1000))
    run_interval: Mapped[timedelta] = mapped_column(INTERVAL(), index=True)
    enabled: Mapped[bool] = mapped_column(BOOLEAN(), index=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), index=True, server_default=text("now()"))

    __table_args__ = (UniqueConstraint("user_id", "url"),)
