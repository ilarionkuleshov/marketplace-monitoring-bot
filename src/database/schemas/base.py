from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base for all schemas."""

    model_config = ConfigDict(from_attributes=True)


def validate_at_least_one_field_not_none(values: dict[str, Any]) -> dict[str, Any]:
    """Returns field `values` after validation that at least one value is not none.

    Raises:
        ValueError: All field values is None.

    """
    not_none_values = [value for value in values.values() if value is not None]
    if not_none_values:
        return values
    raise ValueError("All field values is None")
