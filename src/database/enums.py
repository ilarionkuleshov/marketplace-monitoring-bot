from enum import StrEnum


class DatabaseEnum(StrEnum):
    """Base for database enums."""

    @classmethod
    def values(cls) -> list[str]:
        """Get all values of the enum."""
        return [member.value for member in cls]


class UserLanguage(DatabaseEnum):
    """Supported user languages."""

    EN: str = "en"
