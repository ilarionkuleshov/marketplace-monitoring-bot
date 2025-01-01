from typing import Any

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from bot.middlewares import ApiProvider
from database.schemas import MarketplaceRead


async def get_marketplaces_keyboard(
    api: ApiProvider, provide_id: bool, provide_url: bool
) -> InlineKeyboardMarkup | None:
    """Returns a keyboard with available marketplaces.

    Args:
        api (ApiProvider): Provider for the API.
        provide_id (bool): Whether to provide marketplace ID to callback data.
        provide_url (bool): Whether to provide marketplace URL.

    """
    status, marketplaces = await api.request(
        "GET", "/marketplaces/", response_model=MarketplaceRead, response_as_list=True
    )
    if status != 200 or not marketplaces:
        return None

    keyboard_builder = InlineKeyboardBuilder()
    for marketplace in marketplaces:
        kwargs: dict[str, Any] = {"text": marketplace.name}
        if provide_id:
            kwargs["callback_data"] = str(marketplace.id)
        if provide_url:
            kwargs["url"] = marketplace.url
        keyboard_builder.button(**kwargs)

    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()
