"""Common mixins for database models."""

from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import BIGINT, SMALLINT, TIMESTAMP
from sqlalchemy.sql import func

from utils.enums import StatusCodes


class PrimaryKeyMixin:
    """Mixin to add `id` column for the model."""

    id = Column("id", BIGINT(), primary_key=True, autoincrement=True)


class StatusMixin:
    """Mixin to add `status` column for the model."""

    status = Column(
        "status", SMALLINT(), index=True, nullable=False, server_default=text(str(StatusCodes.NOT_PROCESSED.value))
    )


# pylint: disable=E1102
class TimestampAtMixin:
    """Mixin to add `created_at` and `updated_at` column for the model."""

    created_at = Column("created_at", TIMESTAMP(), index=True, nullable=False, server_default=func.current_timestamp())
    updated_at = Column("updated_at", TIMESTAMP(), index=True, nullable=False, server_default=func.current_timestamp())
