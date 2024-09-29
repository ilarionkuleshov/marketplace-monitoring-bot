from datetime import datetime

from pydantic import model_validator

from database.enums import UserLanguage
from database.schemas.base import DatabaseSchema, validate_update_data


class UserRead(DatabaseSchema):
    """User schema for reading."""

    id: int
    language: UserLanguage
    created_at: datetime


class UserCreate(DatabaseSchema):
    """User schema for creation."""

    id: int
    language: UserLanguage | None = None


class UserUpdate(DatabaseSchema):
    """User schema for updating."""

    language: UserLanguage | None = None

    _validate_update_data = model_validator(mode="before")(validate_update_data)
