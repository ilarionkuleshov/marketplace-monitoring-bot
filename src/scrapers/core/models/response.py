from typing import Any

from httpx import URL
from httpx._types import (
    AsyncByteStream,
    HeaderTypes,
    ResponseContent,
    ResponseExtensions,
    SyncByteStream,
)
from pydantic import BaseModel

from scrapers.core.models.request import Request


class Response(BaseModel):
    """Response model."""

    url: URL
    status_code: int
    headers: HeaderTypes | None = None
    content: ResponseContent | None = None
    text: str | None = None
    html: str | None = None
    json: Any | None = None
    stream: SyncByteStream | AsyncByteStream | None = None
    request: Request | None = None
    extensions: ResponseExtensions | None = None
    encoding: str | None = None
