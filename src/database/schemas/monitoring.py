from datetime import datetime, timedelta

from pydantic import AnyHttpUrl, Field, model_validator

from database.schemas.base import DatabaseSchema, validate_update_data


class MonitoringRead(DatabaseSchema):
    """Monitoring schema for reading."""

    id: int
    user_id: int
    marketplace_id: int
    name: str
    url: str
    run_interval: timedelta
    enabled: bool
    created_at: datetime


class MonitoringCreate(DatabaseSchema):
    """Monitoring schema for creation."""

    user_id: int
    marketplace_id: int
    name: str = Field(max_length=100)
    url: AnyHttpUrl = Field(max_length=2000)
    run_interval: timedelta
    enabled: bool | None = None


class MonitoringUpdate(DatabaseSchema):
    """Monitoring schema for updating."""

    name: str | None = Field(default=None, max_length=100)
    url: AnyHttpUrl | None = Field(default=None, max_length=2000)
    run_interval: timedelta | None = None
    enabled: bool | None = None

    _validate_update_data = model_validator(mode="before")(validate_update_data)
