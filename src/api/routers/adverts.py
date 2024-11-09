from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from database import DatabaseProvider, get_database_provider
from database.models import Advert
from database.schemas import AdvertRead

router = APIRouter(prefix="/adverts")


@router.get("/")
async def read_adverts(database: Annotated[DatabaseProvider, Depends(get_database_provider)]) -> list[AdvertRead]:
    """Returns all adverts.

    Args:
        database (DatabaseProvider): Provider for the database.

    """
    return await database.get_all(model=Advert, read_schema=AdvertRead)


@router.get("/{advert_id}")
async def read_advert(
    advert_id: int, database: Annotated[DatabaseProvider, Depends(get_database_provider)]
) -> AdvertRead:
    """Returns an advert by ID.

    Args:
        advert_id (int): The ID of the advert.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): If the advert is not found.

    """
    if advert := await database.get(model=Advert, read_schema=AdvertRead, filters=[Advert.id == advert_id]):
        return advert
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Advert not found")
