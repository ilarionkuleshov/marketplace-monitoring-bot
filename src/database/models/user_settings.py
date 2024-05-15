from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import BIGINT, ENUM
from sqlalchemy.orm import Mapped, mapped_column

from database.enums import UserLanguage
from database.models.base import BaseModel


class UserSettings(BaseModel):
    """User settings model."""

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(BIGINT(), primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT(), ForeignKey("users.id"), unique=True)
    language: Mapped[UserLanguage] = mapped_column(
        ENUM(*UserLanguage.values(), name="user_language"), index=True, server_default=text(f"'{UserLanguage.EN}'")
    )
