from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.middlewares import ApiProvider
from bot.utils import get_marketplaces_keyboard
from database.schemas import UserCreate

router = Router(name="common")


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


@router.message(Command("marketplaces"))
async def show_marketplaces(message: Message, api: ApiProvider) -> None:
    """Shows available marketplaces.

    Args:
        message (Message): Message object.
        api (ApiProvider): Provider for the API.

    """
    marketplaces_keyboard = await get_marketplaces_keyboard(api, provide_id=False, provide_url=True)
    if marketplaces_keyboard is None:
        await message.answer("Something went wrong. Please try again later.")
    else:
        await message.answer("Available marketplaces:", reply_markup=marketplaces_keyboard)


@router.message(Command("cancel"))
async def cancel_current_operation(message: Message, state: FSMContext) -> None:
    """Cancels the current operation.

    Args:
        message (Message): Message object.
        state (FSMContext): State context.

    """
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("No active operations to cancel")
        return

    await state.clear()
    await message.answer("Operation canceled")
