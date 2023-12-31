"""Common schemas for API."""

from pydantic import BaseModel


class Detail(BaseModel):
    """Schema with detail message."""

    detail: str
