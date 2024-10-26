from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from settings import ApiSettings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: Annotated[str | None, Depends(api_key_header)]) -> None:
    """Verifies the API key.

    Args:
        api_key (str | None): API key to verify.

    Raises:
        HTTPException (403): If the API key is missing or invalid.

    """
    if api_key is None or api_key != ApiSettings().security_key:
        raise HTTPException(HTTP_403_FORBIDDEN, "Missing or invalid API key")
