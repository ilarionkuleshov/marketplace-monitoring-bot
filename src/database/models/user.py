from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, text
from sqlalchemy.orm import Mapped, mapped_column

from database.enums import UserLanguage
from database.models.base import DatabaseModel


class User(DatabaseModel):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=False)
    language: Mapped[UserLanguage] = mapped_column(
        Enum(*UserLanguage.values(), name="user_language"), index=True, server_default=text(f"'{UserLanguage.EN}'")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, server_default=text("now()"))
