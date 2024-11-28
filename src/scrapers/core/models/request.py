from typing import Any, Callable

from httpx import URL, Timeout
from pydantic import BaseModel, ConfigDict


class Request(BaseModel):
    """Request model."""

    url: URL | str
    callback: Callable  # TODO: complete type hint
    method: str = "GET"
    params: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    cookies: dict[str, str] | None = None
    form_data: dict[str, Any] | None = None
    json_data: Any | None = None
    auth: tuple[str, str] | None = None
    timeout: Timeout = Timeout(10.0)
    follow_redirects: bool = True

    model_config = ConfigDict(arbitrary_types_allowed=True)
