from datetime import datetime, timedelta

from pydantic import Field

from database.enums import MonitoringRunStatus
from database.schemas.base import (
    DatabaseCreateSchema,
    DatabaseReadSchema,
    DatabaseUpdateSchema,
)


class MonitoringRunRead(DatabaseReadSchema):
    """Monitoring run schema for reading."""

    id: int
    monitoring_id: int
    log_file: str | None
    duration: timedelta | None
    status: MonitoringRunStatus
    created_at: datetime


class MonitoringRunCreate(DatabaseCreateSchema):
    """Monitoring run schema for creation."""

    monitoring_id: int
    log_file: str | None = Field(default=None, max_length=200)
    duration: timedelta | None = None
    status: MonitoringRunStatus | None = None


class MonitoringRunUpdate(DatabaseUpdateSchema):
    """Monitoring run schema for updating."""

    log_file: str | None = Field(default=None, max_length=200)
    duration: timedelta | None = None
    status: MonitoringRunStatus | None = None
