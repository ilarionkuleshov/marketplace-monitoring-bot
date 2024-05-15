"""Enums for the database."""

from enum import StrEnum


class BaseStrEnum(StrEnum):
    """Base for database string enums."""

    @classmethod
    def values(cls):
        """Return list of all values of the enum."""
        return [member.value for member in cls]


class UserLanguage(BaseStrEnum):
    """Supported languages for the users."""

    EN: str = "en"
    RU: str = "ru"
    UK: str = "uk"


class RunStatus(BaseStrEnum):
    """Statuses for the runs."""

    SCHEDULED: str = "scheduled"
    RUNNING: str = "running"
    SUCCESS: str = "success"
    FAILED: str = "failed"
