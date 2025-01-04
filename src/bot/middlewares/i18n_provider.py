from typing import Any

from aiogram.exceptions import DetailedAiogramError
from aiogram.types import TelegramObject
from aiogram.utils.i18n.middleware import I18nMiddleware

from database.schemas import UserRead


class I18nProvider(I18nMiddleware):
    """Middleware that provides i18n to the handlers."""

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        """See `I18nMiddleware` class."""
        user = data.get("user")
        if not isinstance(user, UserRead):
            raise DetailedAiogramError("Something went wrong. Please try again later.")
        return str(user.language)
