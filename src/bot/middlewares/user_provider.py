from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.exceptions import DetailedAiogramError
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.middlewares.api_provider import ApiProvider
from database.schemas import UserRead


class UserProvider(BaseMiddleware):
    """Middleware that provides the user to the handlers."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """See `BaseMiddleware` class."""
        api = data.get("api")
        if not isinstance(api, ApiProvider) or not isinstance(event, (Message, CallbackQuery)):
            raise DetailedAiogramError("Something went wrong. Please try again later.")

        user_id = event.chat.id if isinstance(event, Message) else event.from_user.id
        data["user"] = await api.request("GET", f"/users/{user_id}", response_model=UserRead)
        return await handler(event, data)
