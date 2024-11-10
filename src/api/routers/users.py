from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from database import DatabaseProvider, get_database_dep
from database.models import User
from database.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users")


@router.get("/")
async def read_users(database: Annotated[DatabaseProvider, Depends(get_database_dep)]) -> list[UserRead]:
    """Returns a list of all users.

    Args:
        database (DatabaseProvider): Provider for the database.

    """
    return await database.get_all(model=User, read_schema=UserRead)


@router.get("/{user_id}")
async def read_user(user_id: int, database: Annotated[DatabaseProvider, Depends(get_database_dep)]) -> UserRead:
    """Returns a user by id.

    Args:
        user_id (int): The id of the user.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): If the user is not found.

    """
    if user := await database.get(model=User, read_schema=UserRead, filters=[User.id == user_id]):
        return user
    raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")


@router.post("/")
async def create_user(user: UserCreate, database: Annotated[DatabaseProvider, Depends(get_database_dep)]) -> UserRead:
    """Creates a new user.

    Args:
        user (UserCreate): The user to create.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (409): If the user with provided ID already exists.

    Returns:
        UserRead: The created user.

    """
    try:
        return await database.create(model=User, data=user, read_schema=UserRead)
    except IntegrityError:
        raise HTTPException(status.HTTP_409_CONFLICT, "User with this ID already exists")


@router.patch("/{user_id}")
async def update_user(
    user_id: int, user: UserUpdate, database: Annotated[DatabaseProvider, Depends(get_database_dep)]
) -> UserRead:
    """Updates a user.

    Args:
        user_id (int): The id of the user.
        user (UserUpdate): The user data to update.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): If the user is not found.

    Returns:
        UserRead: The updated user.

    """
    try:
        return await database.update(model=User, data=user, read_schema=UserRead, filters=[User.id == user_id])
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")


@router.delete("/{user_id}")
async def delete_user(user_id: int, database: Annotated[DatabaseProvider, Depends(get_database_dep)]) -> dict[str, str]:
    """Deletes a user.

    Args:
        user_id (int): The id of the user.
        database (DatabaseProvider): Provider for the database.

    Raises:
        HTTPException (404): If the user is not found.

    Returns:
        dict[str, str]: The message that the user was deleted.

    """
    try:
        await database.delete(model=User, filters=[User.id == user_id])
        return {"message": "User deleted successfully"}
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
