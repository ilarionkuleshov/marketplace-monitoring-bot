from typing import Any

from httpx import URL
from httpx._types import (
    HeaderTypes,
)
from pydantic import BaseModel

from scrapers.core.models.request import Request


class Response(BaseModel):
    """Response model."""

    url: URL
    status_code: int
    headers: HeaderTypes | None = None
    text: str | None = None
    html: str | None = None
    json_data: Any | None = None
    request: Request | None = None
    encoding: str | None = None
