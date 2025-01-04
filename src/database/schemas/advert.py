from datetime import datetime
from typing import ClassVar

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
    monitoring_run_id: int
    url: str
    title: str
    description: str | None
    image: str | None
    price: float | None
    max_price: float | None
    currency: str | None
    sent_to_user: bool
    created_at: datetime
    updated_at: datetime


class AdvertCreate(DatabaseCreateSchema):
    """Advert schema for creation."""

    monitoring_id: int
    monitoring_run_id: int
    url: StrHttpUrl = Field(max_length=2000)
    title: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=300)
    image: str | None = Field(default=None, max_length=2000)
    price: float | None = None
    max_price: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)

    unique_fields: ClassVar[list[str]] = ["monitoring_id", "url"]
    update_fields: ClassVar[list[str]] = [
        "monitoring_run_id",
        "title",
        "description",
        "image",
        "price",
        "max_price",
        "currency",
    ]


class AdvertUpdate(DatabaseUpdateSchema):
    """Advert schema for updating."""

    monitoring_run_id: int | None = None
    title: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    image: str | None = Field(default=None, max_length=2000)
    price: float | None = None
    max_price: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    sent_to_user: bool | None = None
