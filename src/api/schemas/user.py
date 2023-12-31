"""Schemas for user entity."""

from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, root_validator

from api.schemas.base import SchemaWithExample
from api.utils.validators import check_at_least_one_parameter_not_none
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
    def validate_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Returns field `values` after validation."""
        check_at_least_one_parameter_not_none(**values)
        return values

    @classmethod
    def example(cls) -> Self:
        """See `SchemaWithExample` class."""
        return cls(
            name="example_name",
            language=BotLanguages.EN,
        )
