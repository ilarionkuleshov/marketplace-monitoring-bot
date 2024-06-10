"""Auth dependency."""

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from settings import ApiSettings

api_key_header = APIKeyHeader(name="X-API-Key")


def verify_api_key(api_key: str = Security(api_key_header)) -> None:
    """Verifies `api_key`.

    Raises:
        HTTPException (403): Invalid API key.

    """
    if api_key != ApiSettings().key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
