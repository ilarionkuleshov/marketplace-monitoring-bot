from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.middlewares import ApiProvider
from database.schemas import MarketplaceRead

router = Router(name="marketplaces")


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
