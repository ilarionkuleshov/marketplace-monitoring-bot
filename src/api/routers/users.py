from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from database import DatabaseProvider
from database.models import User
from database.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users")


@router.get("/")
async def read_users(database: Annotated[DatabaseProvider, Depends()]) -> list[UserRead]:
    """Returns all users from the database.

    Args:
        database (DatabaseProvider): Provider for the database.

    """
    return await database.get_all(model=User, return_schema=UserRead)


@router.get("/{user_id}")
async def read_user(user_id: int, database: Annotated[DatabaseProvider, Depends()]) -> UserRead:
    """Returns user by id from the database.

    Args:
        user_id (int): Id of the user to get.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): User not found.

    """
    if user := await database.get(model=User, conditions=[User.id == user_id], return_schema=UserRead):
        return user
    raise HTTPException(HTTP_404_NOT_FOUND, "User not found")


@router.post("/")
async def create_user(user: UserCreate, database: Annotated[DatabaseProvider, Depends()]) -> UserRead:
    """Returns created user in the database.

    Args:
        user (UserCreate): User to create.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (409): User with this id already exists in the database.

    """
    try:
        return await database.create(model=User, data=user, return_schema=UserRead)
    except IntegrityError as error:
        raise HTTPException(HTTP_409_CONFLICT, "User with this id already exists in the database") from error


@router.patch("/{user_id}")
async def update_user(user_id: int, user: UserUpdate, database: Annotated[DatabaseProvider, Depends()]) -> UserRead:
    """Returns updated user in the database.

    Args:
        user_id (int): Id of the user to update.
        user (UserUpdate): User to update.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): User not found.

    """
    try:
        return await database.update(model=User, data=user, conditions=[User.id == user_id], return_schema=UserRead)
    except ValueError as error:
        raise HTTPException(HTTP_404_NOT_FOUND, "User not found") from error


@router.delete("/{user_id}")
async def delete_user(user_id: int, database: Annotated[DatabaseProvider, Depends()]) -> None:
    """Deletes user from the database.

    Args:
        user_id (int): Id of the user to delete.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): User not found.

    """
    try:
        await database.delete(model=User, conditions=[User.id == user_id])
    except ValueError as error:
        raise HTTPException(HTTP_404_NOT_FOUND, "User not found") from error
