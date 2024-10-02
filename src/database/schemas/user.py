from datetime import datetime

from database.enums import UserLanguage
from database.schemas.base import (
    DatabaseCreateSchema,
    DatabaseReadSchema,
    DatabaseUpdateSchema,
)


class UserRead(DatabaseReadSchema):
    """User schema for reading."""

    id: int
    language: UserLanguage
    created_at: datetime


class UserCreate(DatabaseCreateSchema):
    """User schema for creation."""

    id: int
    language: UserLanguage | None = None


class UserUpdate(DatabaseUpdateSchema):
    """User schema for updating."""

    language: UserLanguage | None = None
