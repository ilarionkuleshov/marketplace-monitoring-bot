from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n.core import I18n

from bot.middlewares import ApiProvider
from bot.utils.keyboards import get_marketplaces_keyboard
from database.schemas import UserCreate

router = Router(name="common")


@router.message(CommandStart())
async def register_user(message: Message, api: ApiProvider, i18n: I18n) -> None:
    """Registers new user and sends a welcome message.

    Args:
        message (Message): Message object.
        api (ApiProvider): Provider for the API.
        i18n (I18n): I18n object.

    """
    await api.request("POST", "/users/", json_data=UserCreate(id=message.chat.id), acceptable_statuses=[200, 409])
    await message.answer(
        i18n.gettext(
            "Hello! I'm marketplace monitoring bot. I can help you to monitor adverts on different marketplaces."
        )
    )


@router.message(Command("marketplaces"))
async def show_marketplaces(message: Message, api: ApiProvider, i18n: I18n) -> None:
    """Shows available marketplaces.

    Args:
        message (Message): Message object.
        api (ApiProvider): Provider for the API.
        i18n (I18n): I18n object.

    """
    marketplaces_keyboard = await get_marketplaces_keyboard(api, provide_id=False, provide_url=True)
    await message.answer(i18n.gettext("Available marketplaces:"), reply_markup=marketplaces_keyboard)


@router.message(Command("cancel"))
async def cancel_current_operation(message: Message, state: FSMContext, i18n: I18n) -> None:
    """Cancels the current operation.

    Args:
        message (Message): Message object.
        state (FSMContext): State context.
        i18n (I18n): I18n object.

    """
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(i18n.gettext("No active operations to cancel"))
        return

    await state.clear()
    await message.answer(i18n.gettext("Operation canceled"))
