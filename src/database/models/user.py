from datetime import datetime

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import BIGINT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import BaseModel


class User(BaseModel):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BIGINT(), primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT(), unique=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), index=True, server_default=text("now()"))
