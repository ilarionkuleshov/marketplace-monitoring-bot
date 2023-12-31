"""Schemas for search task entity."""

from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, ConfigDict

from api.schemas.base import SchemaWithExample


class SearchTask(BaseModel):
    """Search task schema."""

    id: int
    search_query_id: int
    log_file: str | None
    statistics: dict[str, Any] | None
    status: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchTaskCreate(SchemaWithExample):
    """Schema to create search task."""

    search_query_id: int

    @classmethod
    def example(cls) -> Self:
        """See `SchemaWithExample` class."""
        return cls(search_query_id=1)
