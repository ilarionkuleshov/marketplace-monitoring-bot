from typing import Annotated

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from settings import ApiConfig

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def verify_api_key(api_key: Annotated[str | None, Security(api_key_header)]) -> None:
    """Verifies API key.

    Args:
        api_key (str | None): API key to verify.

    Raises:
        HTTPException (403): Missing or invalid API key.

    """
    if api_key is None or api_key != ApiConfig().security_key:
        raise HTTPException(HTTP_403_FORBIDDEN, "Missing or invalid API key")
