from typing import Any

from httpx import URL
from httpx._config import DEFAULT_TIMEOUT_CONFIG
from httpx._types import (
    AsyncByteStream,
    AuthTypes,
    CertTypes,
    CookieTypes,
    HeaderTypes,
    ProxiesTypes,
    ProxyTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestExtensions,
    RequestFiles,
    SyncByteStream,
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
    content: RequestContent | None = None
    data: RequestData | None = None
    files: RequestFiles | None = None
    json: Any | None = None
    stream: SyncByteStream | AsyncByteStream | None = None
    extensions: RequestExtensions | None = None
    auth: AuthTypes | None = None
    proxy: ProxyTypes | None = None
    proxies: ProxiesTypes | None = None
    timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG
    follow_redirects: bool = True
    verify: VerifyTypes = True
    cert: CertTypes | None = None
    trust_env: bool = False
