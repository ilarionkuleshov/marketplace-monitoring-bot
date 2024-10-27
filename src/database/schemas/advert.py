from datetime import datetime

from pydantic import Field

from database.schemas.base import (
    DatabaseCreateSchema,
    DatabaseReadSchema,
    DatabaseUpdateSchema,
    StrHttpUrl,
)


class AdvertRead(DatabaseReadSchema):
    """Advert schema for reading."""

    id: int
    monitoring_id: int
    url: str
    title: str
    description: str | None
    image: str | None
    price: float | None
    max_price: float | None
    currency: str | None
    created_at: datetime
    updated_at: datetime


class AdvertCreate(DatabaseCreateSchema):
    """Advert schema for creation."""

    monitoring_id: int
    url: StrHttpUrl = Field(max_length=2000)
    title: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=300)
    image: str | None = Field(default=None, max_length=2000)
    price: float | None = None
    max_price: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)


class AdvertUpdate(DatabaseUpdateSchema):
    """Advert schema for updating."""

    title: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    image: str | None = Field(default=None, max_length=2000)
    price: float | None = None
    max_price: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
