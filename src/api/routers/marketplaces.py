"""Router for marketplaces."""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import verify_api_key
from database import DatabaseProvider
from database.models import Marketplace
from database.schemas import MarketplaceRead

router = APIRouter(prefix="/marketplaces", dependencies=[Depends(verify_api_key)])


@router.get("")
async def read_marketplaces(database: Annotated[DatabaseProvider, Depends()]) -> list[MarketplaceRead]:
    """Returns all marketplaces.

    Args:
        database (DatabaseProvider): Provider for the database.

    """
    return await database.get_all(Marketplace, schema=MarketplaceRead)
