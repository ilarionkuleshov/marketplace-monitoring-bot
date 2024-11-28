import asyncio
import logging
from abc import ABC, abstractmethod
from asyncio import Task
from typing import AsyncGenerator

from httpx import AsyncClient

from scrapers.core.models import Request, Response


class Crawler(ABC):
    """Base for all crawlers.

    Attributes:
        logger (logging.Logger): Logger for the crawler.

    """

    logger: logging.Logger
    _request_tasks: list[Task]

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._request_tasks = []

    @abstractmethod
    async def generate_requests(self) -> AsyncGenerator[Request, None]:
        """Yields requests to be processed."""
        if False:  # pylint: disable=W0125
            yield Request(url="https://example.com", callback=lambda _: None)  # just a stub for mypy

    async def run(self) -> None:
        """Runs the crawler."""
        async for request in self.generate_requests():
            self._create_request_task(request)
        await asyncio.gather(*self._request_tasks)

    def _create_request_task(self, request: Request) -> None:
        """Creates a task to handle the `request`."""
        task = asyncio.create_task(self._handle_request(request))
        self._request_tasks.append(task)

    async def _handle_request(self, request: Request) -> None:
        """Handles the `request`."""
        self.logger.debug("Request: %s, %s", request.method, request.url)

        async with AsyncClient() as client:
            httpx_response = await client.request(
                url=request.url,
                method=request.method,
                params=request.params,
                headers=request.headers,
                cookies=request.cookies,
                data=request.form_data,
                json=request.json_data,
                auth=request.auth,
                timeout=request.timeout,
                follow_redirects=request.follow_redirects,
            )

        response = Response.from_httpx_response(httpx_response, request)
        self.logger.debug("Response: %s, %s", response.status_code, response.url)

        callback_result = await request.callback(response)
        if hasattr(callback_result, "__aiter__"):
            async for item in callback_result:
                if isinstance(item, Request):
                    self._create_request_task(item)
