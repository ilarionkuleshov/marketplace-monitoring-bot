from typing import Optional


class SingletonBase:
    """Base for the `singleton` classes."""

    _instance: Optional["SingletonBase"] = None

    def __new__(cls, *args, **kwargs) -> "SingletonBase":
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
