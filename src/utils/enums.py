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


class Marketplaces(StrEnum):
    """Available marketplaces."""

    SHAFA: str = "Shafa.ua"
    OLX: str = "Olx.ua"
    WORK: str = "Work.ua"
    ROBOTA: str = "Robota.ua"
    DOU_JOBS: str = "Jobs.dou.ua"


class MarketplaceSpiders(StrEnum):
    """Spiders for marketplaces."""

    SHAFA: str = "shafa"
    OLX: str = "olx"
    WORK: str = "work"
    ROBOTA: str = "robota"
    DOU_JOBS: str = "dou_jobs"
