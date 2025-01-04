from typing import Any

from aiogram.exceptions import DetailedAiogramError
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram.utils.i18n.middleware import I18nMiddleware
from babel import Locale, UnknownLocaleError

from bot.middlewares.api_provider import ApiProvider
from database.schemas import UserRead


class I18nProvider(I18nMiddleware):
    """Middleware that provides i18n to the handlers."""

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        """See `I18nMiddleware` class."""
        if isinstance(event, Message):
            user_id = event.chat.id
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            user = event.from_user
        else:
            return self.i18n.default_locale

        api = data.get("api")
        language_code = user.language_code if user else None

        if isinstance(api, ApiProvider):
            try:
                language_code = str((await api.request("GET", f"/users/{user_id}", response_model=UserRead)).language)
            except DetailedAiogramError:
                ...

        if language_code is None:
            return self.i18n.default_locale
        try:
            locale = Locale.parse(language_code)
        except UnknownLocaleError:
            return self.i18n.default_locale

        if locale.language not in self.i18n.available_locales:
            return self.i18n.default_locale
        return locale.language
