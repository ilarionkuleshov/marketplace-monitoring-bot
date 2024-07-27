from datetime import datetime

from pydantic import Field, model_validator

from database.enums import RunStatus
from database.schemas.base import BaseSchema, validate_at_least_one_field_not_none


class MonitoringRunRead(BaseSchema):
    """Monitoring run read schema."""

    id: int
    monitoring_id: int
    log_file: str | None
    status: RunStatus
    created_at: datetime


class MonitoringRunCreate(BaseSchema):
    """Monitoring run create schema."""

    monitoring_id: int
    log_file: str | None = Field(default=None, min_length=1, max_length=100)
    status: RunStatus | None = None


class MonitoringRunUpdate(BaseSchema):
    """Monitoring run update schema."""

    log_file: str | None = Field(default=None, min_length=1, max_length=100)
    status: RunStatus | None = None

    _validate_at_least_one_field_not_none = model_validator(mode="before")(validate_at_least_one_field_not_none)
