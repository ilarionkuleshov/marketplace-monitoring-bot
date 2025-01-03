from datetime import datetime, timedelta


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
def get_readable_time_ago(dt: datetime) -> str:
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


def get_timedelta_from_callback_data(data: str) -> timedelta:
    """Returns a timedelta object from callback data.

    Args:
        data (str): Callback data.

    """
    return timedelta(seconds=float(data))
