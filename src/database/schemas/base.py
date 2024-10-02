from abc import ABC
from typing import Annotated, Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, PlainSerializer, model_validator


class DatabaseReadSchema(BaseModel, ABC):
    """Base for database read schemas."""

    model_config = ConfigDict(from_attributes=True)


class DatabaseCreateSchema(BaseModel, ABC):
    """Base for database create schemas."""

    def model_dump_for_insert(self) -> dict[str, Any]:
        """Returns the data to insert."""
        return self.model_dump(exclude_none=True)


class DatabaseUpdateSchema(BaseModel, ABC):
    """Base for database update schemas."""

    def model_dump_for_update(self) -> dict[str, Any]:
        """Returns the data to update."""
        return self.model_dump(exclude_none=True)

    @model_validator(mode="before")
    def validate_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Returns `data` after validation.

        Raises:
            ValueError: All values are None, no data to update.

        """
        not_none_values = [value for value in data.values() if value is not None]
        if not_none_values:
            return data
        raise ValueError("All values are None, no data to update")


StrHttpUrl = Annotated[AnyHttpUrl, PlainSerializer(str)]
