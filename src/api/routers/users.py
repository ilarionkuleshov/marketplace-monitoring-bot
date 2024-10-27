from typing import Annotated

from fastapi import APIRouter, Depends

from database import DatabaseProvider
from database.models import User
from database.schemas import UserRead

router = APIRouter(prefix="/users")


@router.get("/")
async def read_users(database: Annotated[DatabaseProvider, Depends()]) -> list[UserRead]:
    """Returns a list of all users.

    Args:
        database (DatabaseProvider): Provider for the database.

    """
    return await database.get_all(model=User, read_schema=UserRead)
