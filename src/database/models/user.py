from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import BIGINT, VARCHAR

from database.models.base import Base, PrimaryKeyMixin, TimestampAtMixin
from utils.enums import BotLanguages


class User(Base, PrimaryKeyMixin, TimestampAtMixin):
    """Telegram user model."""

    __tablename__ = "users"

    telegram_id = Column("telegram_id", BIGINT(), unique=True, nullable=False)
    name = Column("name", VARCHAR(500), nullable=False)
    language = Column("language", VARCHAR(2), nullable=False, server_default=text(f"'{BotLanguages.EN}'"))
