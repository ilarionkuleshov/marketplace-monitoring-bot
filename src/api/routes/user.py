"""Routes for the interacting with user entities."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from api.dependencies import DatabaseProvider
from api.schemas import User, UserCreate, UserUpdate
from database.models import User as UserModel


async def read_user(telegram_id: int, db_provider: DatabaseProvider = Depends(DatabaseProvider)) -> User:
    """Returns user from the database.

    Args:
        telegram_id (int): Telegram id of the user to get.
        db_provider (DatabaseProvider): Provider for database.

    Raises:
        HTTPException: User with the given `telegram_id` not found.

    """
    query = select(UserModel).where(UserModel.telegram_id == telegram_id)
    if user := await db_provider.select(query, fetch_all=False):
        return User.model_validate(user[0])
    raise HTTPException(status.HTTP_404_NOT_FOUND, f"User with Telegram ID {telegram_id} not found")


async def create_user(user: UserCreate, db_provider: DatabaseProvider = Depends(DatabaseProvider)) -> User:
    """Creates user in the database.

    Args:
        user (UserCreate): User to create.
        db_provider (DatabaseProvider): Provider for database.

    Returns:
        User: Created user.

    Raises:
        HTTPException: User with the given `telegram_id` already exists in database.

    """
    query = insert(UserModel).values(user.model_dump())
    user_id = await db_provider.insert(query)
    if user_id is not None:
        return await read_user(telegram_id=user.telegram_id, db_provider=db_provider)
    raise HTTPException(status.HTTP_409_CONFLICT, f"User with Telegram ID {user.telegram_id} already exists")


async def update_user(
    telegram_id: int, user: UserUpdate, db_provider: DatabaseProvider = Depends(DatabaseProvider)
) -> User:
    """Updates user in the database.

    Args:
        telegram_id (int): Telegram id of the user to update.
        user (UserUpdate): User data to update.
        db_provider (DatabaseProvider): Provider for database.

    Returns:
        User: Updated user.

    """
    query = update(UserModel).where(UserModel.telegram_id == telegram_id).values(user.model_dump(exclude_none=True))
    await db_provider.execute(query)
    return await read_user(telegram_id=telegram_id, db_provider=db_provider)


async def delete_user(telegram_id: int, db_provider: DatabaseProvider = Depends(DatabaseProvider)) -> None:
    """Deletes user from the database.

    Args:
        telegram_id (int): Telegram id of the user to delete.
        db_provider (DatabaseProvider): Provider for database.

    """
    query = delete(UserModel).where(UserModel.telegram_id == telegram_id)
    await db_provider.execute(query)


def setup(router: APIRouter) -> None:
    """Adds user routes for the FastAPI `router`."""
    router.add_api_route("/user/", read_user, methods=["GET"], response_model=User)
    router.add_api_route("/user/", create_user, methods=["POST"], response_model=User)
    router.add_api_route("/user/", update_user, methods=["PATCH"], response_model=User)
    router.add_api_route("/user/", delete_user, methods=["DELETE"], response_model=None)
