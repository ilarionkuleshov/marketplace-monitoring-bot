"""Router for users."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import verify_api_key
from database import DatabaseProvider
from database.models import User
from database.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", dependencies=[Depends(verify_api_key)])


@router.get("")
async def read_users(database: Annotated[DatabaseProvider, Depends()]) -> list[UserRead]:
    """Returns all users.

    Args:
        database (DatabaseProvider): Provider for the database.

    """
    return await database.get_all(User, schema=UserRead)


@router.get("/{user_id}")
async def read_user(user_id: int, database: Annotated[DatabaseProvider, Depends()]) -> UserRead:
    """Returns user by id.

    Args:
        user_id (int): Id of the user to get.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): User not found.

    """
    if user := await database.get(User, conditions=[User.id == user_id], schema=UserRead):
        return user
    raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")


@router.post("")
async def create_user(user: UserCreate, database: Annotated[DatabaseProvider, Depends()]) -> UserRead:
    """Creates user.

    Args:
        user (UserCreate): User to create.
        database (DatabaseProvider): Provider for the database.

    """
    return await database.create(User(**user.model_dump()), schema=UserRead)


@router.patch("/{user_id}")
async def update_user(user_id: int, user: UserUpdate, database: Annotated[DatabaseProvider, Depends()]) -> UserRead:
    """Returns updated user.

    Args:
        user_id (int): Id of the user to update.
        user (UserUpdate): User data to update.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): User not found.

    """
    if updated_user := await database.update(
        User, data=user.model_dump(), conditions=[User.id == user_id], schema=UserRead
    ):
        return updated_user
    raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
