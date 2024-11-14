from typing import Any

from httpx import URL, Timeout
from httpx._types import (
    AuthTypes,
    CertTypes,
    CookieTypes,
    HeaderTypes,
    ProxyTypes,
    QueryParamTypes,
    RequestData,
    RequestFiles,
    TimeoutTypes,
    VerifyTypes,
)
from pydantic import BaseModel


class Request(BaseModel):
    """Request model."""

    url: URL | str
    method: str = "GET"
    params: QueryParamTypes | None = None
    headers: HeaderTypes | None = None
    cookies: CookieTypes | None = None
    form_data: RequestData | None = None
    json_data: Any | None = None
    files: RequestFiles | None = None
    auth: AuthTypes | None = None
    proxy: ProxyTypes | None = None
    timeout: TimeoutTypes = Timeout(10.0)
    follow_redirects: bool = True
    verify: VerifyTypes = True
    cert: CertTypes | None = None
