from pydantic import ValidationError
from pydantic.networks import AnyHttpUrl


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
