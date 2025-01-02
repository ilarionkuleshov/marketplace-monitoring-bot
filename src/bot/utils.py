from datetime import datetime, timedelta
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


def get_timedelta_frequency(td: timedelta) -> str:
    """Returns a human-readable string representing the frequency of a timedelta.

    Timedelta is considered to be a multiple of minutes or hours.

    Args:
        td (timedelta): Timedelta object.

    """
    total_seconds = int(td.total_seconds())

    if total_seconds % 60 == 0:
        minutes = total_seconds // 60
        if minutes == 1:
            return "every 1 min"
        return f"every {minutes} min"

    hours = total_seconds // 3600
    if hours == 1:
        return "every 1 hour"
    return f"every {hours} hours"


# pylint: disable=R0911
def get_time_ago(dt: datetime) -> str:
    """Returns a human-readable string representing the time ago.

    Args:
        dt (datetime): Datetime object.

    """
    delta = datetime.now(tz=dt.tzinfo) - dt

    if delta < timedelta(minutes=1):
        return "just now"

    if delta < timedelta(hours=1):
        minutes = delta.total_seconds() // 60
        return f"{int(minutes)} min ago" if minutes > 1 else "1 min ago"

    if delta < timedelta(days=1):
        hours = delta.total_seconds() // 3600
        return f"{int(hours)} hours ago" if hours > 1 else "1 hour ago"

    if delta < timedelta(days=7):
        days = delta.days
        return f"{days} days ago" if days > 1 else "1 day ago"

    if delta < timedelta(days=30):
        weeks = delta.days // 7
        return f"{weeks} weeks ago" if weeks > 1 else "1 week ago"

    if delta < timedelta(days=365):
        months = delta.days // 30
        return f"{months} months ago" if months > 1 else "1 month ago"

    years = delta.days // 365
    return f"{years} years ago" if years > 1 else "1 year ago"
