from typing import Any

from pydantic import BaseModel, ConfigDict


class DatabaseSchema(BaseModel):
    """Base for database schemas."""

    model_config = ConfigDict(from_attributes=True)


def validate_update_data(data: dict[str, Any]) -> Any:
    """Returns validated update `data`.

    Raises:
        ValueError: All values are None, no data to update.

    """
    not_none_values = [value for value in data.values() if value is not None]
    if not_none_values:
        return data
    raise ValueError("All values are None, no data to update")
