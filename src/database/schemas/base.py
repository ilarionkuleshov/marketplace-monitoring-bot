from typing import Any

from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Base for all schemas."""


def validate_at_least_one_field_not_none(fields: dict[str, Any]) -> dict[str, Any]:
    """Returns `fields` after validation that at least one field is not none.

    Raises:
        ValueError: All field values is None.

    """
    not_none_values = [value for value in fields.values() if value is not None]
    if not_none_values:
        return fields
    raise ValueError("All field values is None")
