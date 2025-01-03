from typing import Any, Awaitable, Callable, Literal, overload

from aiogram import BaseMiddleware
from aiogram.exceptions import DetailedAiogramError
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
        acceptable_statuses: list[int] | None = None,
        custom_error_messages: dict[int, str] | None = None,
    ) -> None: ...

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
        acceptable_statuses: list[int] | None = None,
        custom_error_messages: dict[int, str] | None = None,
    ) -> T: ...

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
        acceptable_statuses: list[int] | None = None,
        custom_error_messages: dict[int, str] | None = None,
    ) -> list[T]: ...

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
        acceptable_statuses: list[int] | None = None,
        custom_error_messages: dict[int, str] | None = None,
    ) -> (T | list[T] | None):
        """Makes a request to the API.

        Args:
            method (str): The HTTP method.
            url (str): The URL.
            query_params (dict[str, Any] | None): The query parameters. Default is None.
            json_data (PydanticModel | None): The data to send. Default is None.
            response_model (type[T] | None): Model for response item(s). Default is None.
            response_as_list (bool): Whether to return response as list. Default is False.
            acceptable_statuses (list[int] | None): The acceptable statuses.
                If the response status code is not in this list, exception will be raised.
                If not provided, [200] will be used. Default is None.
            custom_error_messages (dict[int, str] | None): Custom error messages for statuses. Default is None.

        Returns:
            T: Response item if response_model provided and response_as_list is False.
            list[T]: Response items if response_model provided and response_as_list is True.
            None: If response_model is not provided.

        """
        kwargs: dict[str, Any] = {"method": method, "url": url}
        if query_params:
            kwargs["params"] = query_params
        if json_data:
            kwargs["json"] = json_data.model_dump(mode="json")
        response = await self._client.request(**kwargs)

        acceptable_statuses = acceptable_statuses or [200]
        if response.status_code not in acceptable_statuses:
            custom_error_messages = custom_error_messages or {}
            error_message = custom_error_messages.get(
                response.status_code, "Something went wrong. Please try again later."
            )
            raise DetailedAiogramError(error_message)

        if response_model is None:
            return None

        response_json = response.json()
        if response_as_list:
            return [response_model.model_validate(item) for item in response_json]
        return response_model.model_validate(response_json)
