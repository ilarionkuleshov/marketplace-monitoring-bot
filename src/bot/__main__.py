import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import DetailedAiogramError
from aiogram.filters import ExceptionTypeFilter
from aiogram.utils.i18n.core import I18n

from bot.errors import handle_detailed_error
from bot.middlewares import ApiProvider, I18nProvider, UserProvider
from bot.routers import (
    common_router,
    my_monitorings_router,
    new_monitoring_router,
    settings_router,
)
from settings import BotSettings


def setup_middlewares(dp: Dispatcher) -> None:
    """Sets up the middlewares for the Aiogram Dispatcher."""
    dp.message.middleware(ApiProvider())
    dp.callback_query.middleware(ApiProvider())

    dp.message.middleware(UserProvider())
    dp.callback_query.middleware(UserProvider())

    i18n = I18n(path="bot/locales")
    dp.message.middleware(I18nProvider(i18n))
    dp.callback_query.middleware(I18nProvider(i18n))


def setup_error_handlers(dp: Dispatcher) -> None:
    """Sets up the error handlers for the Aiogram Dispatcher."""
    dp.errors(ExceptionTypeFilter(DetailedAiogramError), F.update.message.as_("message"))(handle_detailed_error)
    dp.errors(ExceptionTypeFilter(DetailedAiogramError), F.update.callback_query.as_("callback"))(handle_detailed_error)


async def main() -> None:
    """Runs the Aiogram application."""
    bot_settings = BotSettings()
    logging.basicConfig(level=bot_settings.log_level)

    bot = Bot(token=bot_settings.token)
    dp = Dispatcher()

    setup_middlewares(dp)
    setup_error_handlers(dp)
    dp.include_routers(common_router, new_monitoring_router, my_monitorings_router, settings_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
