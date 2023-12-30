"""Schemas for search task entity."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from api.schemas.base import SchemaWithExample


class SearchTask(BaseModel):
    """Search task schema."""

    id: int
    search_query_id: int
    log_file: str
    statistics: dict[str, Any]
    status: int
    created_at: datetime
    updated_at: datetime


class SearchTaskCreate(SchemaWithExample):
    """Schema to create search task."""

    search_query_id: int
