from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.middlewares import ApiProvider
from database.schemas import MarketplaceRead, UserCreate

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
    # pylint: disable=R0801
    status, marketplaces = await api.request(
        "GET", "/marketplaces/", response_model=MarketplaceRead, response_as_list=True
    )
    if status != 200 or not marketplaces:
        await message.answer("Something went wrong. Please try again later.")
        return
    await message.answer(
        text="Available marketplaces:\n"
        + "\n".join([f"[*{marketplace.name}*]({marketplace.url})" for marketplace in marketplaces]),
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )


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
