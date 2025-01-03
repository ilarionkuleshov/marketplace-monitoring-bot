from datetime import datetime, timedelta
from typing import Any

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from pydantic import ValidationError
from pydantic.networks import AnyHttpUrl

from bot.middlewares import ApiProvider
from database.schemas import MarketplaceRead, MonitoringUpdate


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


def get_readable_timedelta(td: timedelta) -> str:
    """Returns a human-readable string representing timedelta.

    Timedelta is considered to be a multiple of minutes or hours.

    Args:
        td (timedelta): Timedelta object.

    """
    total_seconds = int(td.total_seconds())

    if total_seconds < 3600 and total_seconds % 60 == 0:
        minutes = total_seconds // 60
        return f"{minutes}min"

    hours = total_seconds // 3600
    return f"{hours}h"


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


def get_timedelta_from_callback_data(data: str) -> timedelta:
    """Returns a timedelta object from callback data.

    Args:
        data (str): Callback data.

    """
    return timedelta(seconds=float(data))


async def update_monitoring(api: ApiProvider, monitoring_id: int, json_data: MonitoringUpdate) -> bool:
    """Updates the monitoring via the API.

    Args:
        api (ApiProvider): Provider for the API.
        monitoring_id (int): Monitoring ID.
        json_data (MonitoringUpdate): Monitoring update data.

    Returns:
        bool: True if the monitoring was updated successfully, False otherwise.

    """
    response_status = await api.request("PATCH", f"/monitorings/{monitoring_id}", json_data=json_data)
    return response_status == 200


def validate_monitoring_name(name: str | None) -> str | None:
    """Validates the monitoring name.

    Args:
        name (str | None): Monitoring name.

    Returns:
        None: Monitoring name is valid.
        str: Error message.

    """
    if not name:
        return "Name is required. Please enter a name."
    if len(name) > 100:
        return "Name is too long. Please enter a shorter name (max 100 characters)."
    return None


def validate_monitoring_url(url: str | None) -> str | None:
    """Validates the monitoring URL.

    Args:
        url (str | None): Monitoring URL.

    Returns:
        None: Monitoring URL is valid.
        str: Error message.

    """
    if not url:
        return "URL is required. Please enter a URL."
    try:
        AnyHttpUrl(url)
    except ValidationError:
        return "Invalid URL. Please enter a valid URL."
    if len(url) > 2000:
        return "URL is too long. Please enter a shorter URL (max 2000 characters)."
    return None
