"""Security dependencies for the API."""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from settings import api_settings

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def validate_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """Checks that `api_key` is valid.

    Raises:
        HTTPException (401): Provided `api_key` is invalid.

    """
    if api_key != str(api_settings().API_KEY):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing or invalid API key")
