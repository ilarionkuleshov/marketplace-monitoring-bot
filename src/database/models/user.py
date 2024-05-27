from datetime import datetime

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import BIGINT, ENUM, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from database.enums import UserLanguage
from database.models.base import BaseModel


class User(BaseModel):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BIGINT(), primary_key=True, autoincrement=False)
    language: Mapped[UserLanguage] = mapped_column(
        ENUM(*UserLanguage.values(), name="user_language"), index=True, server_default=text(f"'{UserLanguage.EN}'")
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), index=True, server_default=text("now()"))
