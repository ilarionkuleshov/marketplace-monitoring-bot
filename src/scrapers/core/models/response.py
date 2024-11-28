from httpx import URL
from httpx import Response as HttpxResponse
from httpx import ResponseNotRead
from pydantic import BaseModel, ConfigDict

from scrapers.core.models.request import Request


class Response(BaseModel):
    """Response model."""

    url: URL
    status_code: int
    content: bytes
    text: str
    headers: dict[str, str] | None = None
    encoding: str | None = None
    request: Request

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_httpx_response(cls, httpx_response: HttpxResponse, request: Request) -> "Response":
        """Returns new instance from an httpx response.

        Args:
            httpx_response (HttpxResponse): Response from httpx.
            request (Request): Request used to fetch the response.

        """
        try:
            content = httpx_response.content
        except ResponseNotRead:
            content = httpx_response.read()

        return cls(
            url=httpx_response.url,
            status_code=httpx_response.status_code,
            content=content,
            text=httpx_response.text,
            headers=httpx_response.headers,
            encoding=httpx_response.encoding,
            request=request,
        )
