from datetime import datetime

from pydantic import model_validator

from database.enums import UserLanguage
from database.schemas.base import BaseSchema, validate_at_least_one_field_not_none


class UserRead(BaseSchema):
    """User read schema."""

    id: int
    language: UserLanguage
    created_at: datetime


class UserCreate(BaseSchema):
    """User create schema."""

    id: int
    language: UserLanguage | None = None


class UserUpdate(BaseSchema):
    """User update schema."""

    language: UserLanguage | None = None

    _validate_at_least_one_field_not_none = model_validator(mode="before")(validate_at_least_one_field_not_none)
