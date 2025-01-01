from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.middlewares import ApiProvider
from database.schemas import UserCreate

router = Router(name="start")


@router.message(CommandStart())
async def register_user(message: Message, api: ApiProvider) -> None:
    """Registers new user and sends a welcome message.

    Args:
        message (Message): Message object.
        api (ApiProvider): Provider for the API.

    """
    status = await api.request("POST", "/users/", json_data=UserCreate(id=message.chat.id))
    if status in [200, 409]:
        await message.answer(
            "Hello! I'm marketplace monitoring bot. I can help you to monitor adverts on different marketplaces."
        )
    else:
        await message.answer("Something went wrong. Please try again later.")
