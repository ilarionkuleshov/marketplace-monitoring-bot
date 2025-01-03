import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import DetailedAiogramError
from aiogram.filters import ExceptionTypeFilter

from bot.errors import handle_detailed_error
from bot.middlewares import ApiProvider
from bot.routers import common_router, my_monitorings_router, new_monitoring_router
from settings import BotSettings


async def main() -> None:
    """Runs the Aiogram application."""
    bot_settings = BotSettings()
    logging.basicConfig(level=bot_settings.log_level)

    bot = Bot(token=bot_settings.token)
    dp = Dispatcher()

    dp.errors(ExceptionTypeFilter(DetailedAiogramError), F.update.message.as_("message"))(handle_detailed_error)
    dp.errors(ExceptionTypeFilter(DetailedAiogramError), F.update.callback_query.as_("callback"))(handle_detailed_error)
    dp.message.middleware(ApiProvider())
    dp.callback_query.middleware(ApiProvider())
    dp.include_routers(common_router, new_monitoring_router, my_monitorings_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
