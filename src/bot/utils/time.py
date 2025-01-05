from datetime import datetime, timedelta

from aiogram.exceptions import DetailedAiogramError
from aiogram.utils.i18n import gettext as get_i18n_text


def get_readable_timedelta(td: timedelta) -> str:
    """Returns a human-readable string representing timedelta.

    Timedelta is considered to be a multiple of minutes or hours.

    Args:
        td (timedelta): Timedelta object.

    """
    total_seconds = int(td.total_seconds())

    if total_seconds < 3600 and total_seconds % 60 == 0:
        minutes = total_seconds // 60
        return get_i18n_text("{minutes}min").format(minutes=minutes)

    hours = total_seconds // 3600
    return get_i18n_text("{hours}h").format(hours=hours)


# pylint: disable=R0911
def get_readable_time_ago(dt: datetime) -> str:
    """Returns a human-readable string representing the time ago.

    Args:
        dt (datetime): Datetime object.

    """
    delta = datetime.now(tz=dt.tzinfo) - dt

    if delta < timedelta(minutes=1):
        return get_i18n_text("just now")

    if delta < timedelta(hours=1):
        minutes = delta.total_seconds() // 60
        return get_i18n_text("{minutes}min ago").format(minutes=int(minutes))

    if delta < timedelta(days=1):
        hours = delta.total_seconds() // 3600
        return get_i18n_text("{hours}h ago").format(hours=int(hours))

    days = delta.days
    return get_i18n_text("{days}d ago").format(days=days)


def get_timedelta_from_callback_data(data: str) -> timedelta:
    """Returns a timedelta object from callback data.

    Args:
        data (str): Callback data.

    """
    try:
        return timedelta(seconds=float(data))
    except ValueError:
        raise DetailedAiogramError(get_i18n_text("Something went wrong. Please try again later."))
