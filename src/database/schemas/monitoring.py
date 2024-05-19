from datetime import datetime, timedelta

from pydantic import Field, HttpUrl, model_validator

from database.schemas.base import BaseSchema, validate_at_least_one_field_not_none


class MonitoringRead(BaseSchema):
    """Monitoring read schema."""

    id: int
    user_id: int
    marketplace_id: int
    name: str
    url: str
    run_interval: timedelta
    enabled: bool
    created_at: datetime


class MonitoringCreate(BaseSchema):
    """Monitoring create schema."""

    user_id: int
    marketplace_id: int
    name: str = Field(min_length=1, max_length=50)
    url: HttpUrl = Field(max_length=1000)
    run_interval: timedelta
    enabled: bool | None = None


class MonitoringUpdate(BaseSchema):
    """Monitoring update schema."""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    url: HttpUrl | None = Field(default=None, max_length=1000)
    run_interval: timedelta | None = None
    enabled: bool | None = None

    _validate_at_least_one_field_not_none = model_validator(mode="before")(validate_at_least_one_field_not_none)
