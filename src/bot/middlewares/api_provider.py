from typing import Any, Awaitable, Callable, Literal, overload

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from httpx import AsyncClient
from pydantic import BaseModel as PydanticModel

from settings import ApiSettings


class ApiProvider(BaseMiddleware):
    """Middleware that provides an API client to the handlers."""

    def __init__(self):
        api_settings = ApiSettings()
        self._client = AsyncClient(base_url=api_settings.get_url(), headers={"X-API-Key": api_settings.security_key})

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """See `BaseMiddleware` class."""
        data["api"] = self
        return await handler(event, data)

    @overload
    async def request(
        self,
        method: str,
        url: str,
        *,
        query_params: dict[str, Any] | None = None,
        json_data: PydanticModel | None = None,
        response_model: None = None,
        response_as_list: bool = False,
    ) -> int: ...

    @overload
    async def request[
        T: PydanticModel
    ](
        self,
        method: str,
        url: str,
        *,
        query_params: dict[str, Any] | None = None,
        json_data: PydanticModel | None = None,
        response_model: type[T],
        response_as_list: Literal[False] = False,
    ) -> tuple[int, T | None]: ...

    @overload
    async def request[
        T: PydanticModel
    ](
        self,
        method: str,
        url: str,
        *,
        query_params: dict[str, Any] | None = None,
        json_data: PydanticModel | None = None,
        response_model: type[T],
        response_as_list: Literal[True] = True,
    ) -> tuple[int, list[T] | None]: ...

    async def request[
        T: PydanticModel
    ](
        self,
        method: str,
        url: str,
        *,
        query_params: dict[str, Any] | None = None,
        json_data: PydanticModel | None = None,
        response_model: type[T] | None = None,
        response_as_list: bool = False,
    ) -> (int | tuple[int, T | list[T] | None]):
        """Makes a request to the API.

        Args:
            method (str): The HTTP method.
            url (str): The URL.
            query_params (dict[str, Any] | None): The query parameters. Default is None.
            json_data (PydanticModel | None): The data to send. Default is None.
            response_model (type[T] | None): The response model.
                If not provided, the response will not be validated. Default is None.
            response_as_list (bool): If the response should be treated as a list. Default is False.

        Returns:
            int: Only the status code if response model is not provided.
            tuple[int, T | list[T] | None]: The status code and response item
                or list of response items if `response_as_list` is True.
                If the request failed, the response item(s) will be None.

        """
        kwargs: dict[str, Any] = {"method": method, "url": url}
        if query_params:
            kwargs["params"] = query_params
        if json_data:
            kwargs["json"] = json_data.model_dump(mode="json")
        response = await self._client.request(**kwargs)

        if response_model is None:
            return response.status_code

        if response.status_code != 200:
            return response.status_code, None

        response_json = response.json()

        if response_as_list:
            return response.status_code, [response_model.model_validate(item) for item in response_json]
        return response.status_code, response_model.model_validate(response_json)
