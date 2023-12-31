"""Validator utilities."""

from fastapi import HTTPException, status


def check_at_least_one_parameter_not_none(**parameters) -> None:
    """Checks that at least one of the `parameters` is not None.

    Raises:
        HTTPException (422): Count of the not None `parameters` is equal to 0.

    """
    if len([value for value in parameters.values() if value is not None]) == 0:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"You must provide at least one of this parameters: {', '.join(parameters)}",
        )


def check_only_one_parameter_not_none(**parameters) -> None:
    """Checks that only one of the `parameters` is not None.

    Raises:
        HTTPException (422): Count of the not None `parameters` not equal to 1.

    """
    if len([value for value in parameters.values() if value is not None]) != 1:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"You must provide one and only one of this parameters: {', '.join(parameters)}",
        )


def check_zero_or_one_parameter_not_none(**parameters) -> None:
    """Checks that zero or one of the `parameters` is not None.

    Raises:
        HTTPException (422): Count of the not None `parameters` greater than 1.

    """
    if len([value for value in parameters.values() if value is not None]) > 1:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"You must provide zero or one of this parameters: {', '.join(parameters)}",
        )
