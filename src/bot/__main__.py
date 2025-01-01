import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.middlewares import ApiProvider
from bot.routers import start_router
from settings import BotSettings


async def main() -> None:
    """Runs the Aiogram application."""
    bot_settings = BotSettings()
    logging.basicConfig(level=bot_settings.log_level)

    bot = Bot(token=bot_settings.token)
    dp = Dispatcher()

    dp.message.middleware(ApiProvider())
    dp.include_routers(start_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())