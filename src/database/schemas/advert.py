from datetime import datetime

from pydantic import Field, HttpUrl, model_validator

from database.schemas.base import BaseSchema, validate_at_least_one_field_not_none


class AdvertRead(BaseSchema):
    """Advert read schema."""

    id: int
    monitoring_id: int
    external_id: str
    url: str
    image: str | None
    title: str
    description: str | None
    price: float | None
    max_price: float | None
    currency: str | None
    created_at: datetime


class AdvertCreate(BaseSchema):
    """Advert create schema."""

    monitoring_id: int
    external_id: str
    url: HttpUrl = Field(max_length=1000)
    image: HttpUrl | None = Field(default=None, max_length=1000)
    title: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=200)
    price: float | None = None
    max_price: float | None = None
    currency: str | None = Field(default=None, min_length=1, max_length=3)


class AdvertUpdate(BaseSchema):
    """Advert update schema."""

    url: HttpUrl | None = Field(default=None, max_length=1000)
    image: HttpUrl | None = Field(default=None, max_length=1000)
    title: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=200)
    price: float | None = None
    max_price: float | None = None
    currency: str | None = Field(default=None, min_length=1, max_length=3)

    _validate_at_least_one_field_not_none = model_validator(mode="before")(validate_at_least_one_field_not_none)
