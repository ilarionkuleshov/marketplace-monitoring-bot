from enum import StrEnum


class BaseStrEnum(StrEnum):
    """Base for database string enums."""

    @classmethod
    def values(cls):
        """Return list of all values of the enum."""
        return [field.value for field in cls]


class UserLanguage(BaseStrEnum):
    """Supported languages for the users."""

    EN: str = "en"
    RU: str = "ru"
    UK: str = "uk"
