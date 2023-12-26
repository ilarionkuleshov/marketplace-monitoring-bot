"""Common enums for the project."""

from enum import IntEnum, StrEnum


class StatusCodes(IntEnum):
    """Status codes for records in DB."""

    NOT_PROCESSED: int = 0
    IN_PROGRESS: int = 1
    SUCCESS: int = 2
    ERROR: int = 4


class BotLanguages(StrEnum):
    """Available languages in telegram bot."""

    EN: str = "en"
