from aiogram import Bot

from settings import BotSettings

bot = Bot(token=BotSettings().token)


async def get_bot() -> Bot:
    """Returns the telegram bot instance."""
    return bot
