from typing import Annotated

from fastapi import APIRouter, Depends

from database import DatabaseProvider
from database.models import Marketplace
from database.schemas import MarketplaceRead

router = APIRouter(prefix="/marketplaces")


@router.get("/")
async def read_marketplaces(database: Annotated[DatabaseProvider, Depends()]) -> list[MarketplaceRead]:
    """Returns a list of all marketplaces.

    Args:
        database (DatabaseProvider): Provider for the database.

    """
    return await database.get_all(model=Marketplace, read_schema=MarketplaceRead)
