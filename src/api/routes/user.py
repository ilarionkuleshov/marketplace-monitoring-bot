"""Routes for the interacting with user entities."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from api.dependencies import DatabaseProvider
from api.schemas import User, UserCreate
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
    if user := await db_provider.select_one(query):
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
    if await db_provider.insert(query):
        return await read_user(telegram_id=user.telegram_id, db_provider=db_provider)
    raise HTTPException(status.HTTP_409_CONFLICT, f"User with Telegram ID {user.telegram_id} already exists")


def setup(router: APIRouter) -> None:
    """Adds user routes for the FastAPI `router`."""
    router.add_api_route("/user/", read_user, methods=["GET"], response_model=User)
    router.add_api_route("/user/", create_user, methods=["POST"], response_model=User)
