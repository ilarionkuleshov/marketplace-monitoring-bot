from datetime import datetime, timedelta

from pydantic import Field, model_validator

from database.enums import MonitoringRunStatus
from database.schemas.base import DatabaseSchema, validate_update_data


class MonitoringRunRead(DatabaseSchema):
    """Monitoring run schema for reading."""

    id: int
    monitoring_id: int
    log_file: str | None
    duration: timedelta | None
    status: MonitoringRunStatus
    created_at: datetime


class MonitoringRunCreate(DatabaseSchema):
    """Monitoring run schema for creation."""

    monitoring_id: int
    log_file: str | None = Field(default=None, max_length=200)
    duration: timedelta | None = None
    status: MonitoringRunStatus | None = None


class MonitoringRunUpdate(DatabaseSchema):
    """Monitoring run schema for updating."""

    log_file: str | None = Field(default=None, max_length=200)
    duration: timedelta | None = None
    status: MonitoringRunStatus | None = None

    _validate_update_data = model_validator(mode="before")(validate_update_data)
