from datetime import datetime, timedelta

from pydantic import Field

from database.schemas.base import (
    DatabaseCreateSchema,
    DatabaseReadSchema,
    DatabaseUpdateSchema,
    StrHttpUrl,
)


class MonitoringRead(DatabaseReadSchema):
    """Monitoring schema for reading."""

    id: int
    user_id: int
    marketplace_id: int
    name: str
    url: str
    run_interval: timedelta
    enabled: bool
    created_at: datetime


class MonitoringCreate(DatabaseCreateSchema):
    """Monitoring schema for creation."""

    user_id: int
    marketplace_id: int
    name: str = Field(max_length=100)
    url: StrHttpUrl = Field(max_length=2000)
    run_interval: timedelta
    enabled: bool | None = None


class MonitoringUpdate(DatabaseUpdateSchema):
    """Monitoring schema for updating."""

    name: str | None = Field(default=None, max_length=100)
    url: StrHttpUrl | None = Field(default=None, max_length=2000)
    run_interval: timedelta | None = None
    enabled: bool | None = None
