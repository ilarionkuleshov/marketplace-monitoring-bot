from abc import ABC, abstractmethod
from typing import Self

from pydantic import BaseModel


class SchemaWithExample(BaseModel, ABC):
    """Base for schemas with `example` method."""

    @classmethod
    @abstractmethod
    def example(cls) -> Self:
        """Returns instance with example values."""
