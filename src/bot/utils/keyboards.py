from datetime import timedelta
from typing import Any

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from bot.middlewares import ApiProvider
from bot.utils.time import get_readable_timedelta
from database.schemas import MarketplaceRead


async def get_marketplaces_keyboard(api: ApiProvider, provide_id: bool, provide_url: bool) -> InlineKeyboardMarkup:
    """Returns a keyboard with available marketplaces.

    Args:
        api (ApiProvider): Provider for the API.
        provide_id (bool): Whether to provide marketplace ID to callback data.
        provide_url (bool): Whether to provide marketplace URL.

    """
    marketplaces = await api.request("GET", "/marketplaces/", response_model=MarketplaceRead, response_as_list=True)

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


def get_run_intervals_keyboard() -> InlineKeyboardMarkup:
    """Returns a keyboard with available run intervals."""
    keyboard_builder = InlineKeyboardBuilder()
    for td in [
        timedelta(minutes=5),
        timedelta(minutes=10),
        timedelta(minutes=15),
        timedelta(minutes=30),
        timedelta(hours=1),
        timedelta(hours=2),
        timedelta(hours=3),
        timedelta(hours=6),
        timedelta(hours=12),
        timedelta(hours=24),
    ]:
        keyboard_builder.button(text=get_readable_timedelta(td), callback_data=str(td.total_seconds()))
    keyboard_builder.adjust(3)
    return keyboard_builder.as_markup()
