from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Start command handler."""
    await message.answer(
        "Hello! I'm marketplace monitoring bot. I can help you to monitor adverts on different marketplaces."
    )
