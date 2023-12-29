"""Schemas for user entity."""

from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, root_validator

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


class UserUpdate(SchemaWithExample):
    """Schema to update user."""

    name: str | None = None
    language: BotLanguages | None = None

    # pylint: disable=E0213
    @root_validator(pre=True)
    def check_at_least_one_field_not_none(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Returns field `values` after validation for at least one field is not None.

        Raises:
            ValueError: All provided field `values` is None.

        """
        if all(value is None for value in values.values()):
            raise ValueError("At least one field must be not null to update user")
        return values

    @classmethod
    def example(cls) -> Self:
        """See `SchemaWithExample` class."""
        return cls(
            name="example_name",
            language=BotLanguages.EN,
        )
