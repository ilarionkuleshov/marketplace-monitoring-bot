"""Schemas for user entity."""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict

from api.schemas.base import SchemaWithExample
from utils.enums import BotLanguages


class User(BaseModel):
    """User schema."""

    id: int
    telegram_id: int
    name: str
    language: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(SchemaWithExample):
    """Schema to create user."""

    telegram_id: int
    name: str
    language: BotLanguages = BotLanguages.EN

    @classmethod
    def example(cls) -> Self:
        """See `SchemaWithExample` class."""
        return cls(
            telegram_id=123456,
            name="example_name",
        )
