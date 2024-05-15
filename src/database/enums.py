"""Enums for the database."""

from enum import StrEnum


class UserLanguage(StrEnum):
    """Supported languages for the users."""

    EN: str = "en"
    RU: str = "ru"
    UK: str = "uk"


class RunStatus(StrEnum):
    """Statuses for the runs."""

    SCHEDULED: str = "scheduled"
    RUNNING: str = "running"
    SUCCESS: str = "success"
    FAILED: str = "failed"
