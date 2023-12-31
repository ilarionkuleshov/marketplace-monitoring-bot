"""Routes for the interacting with user entities."""

# pylint: disable=W0622

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from api.dependencies import DatabaseProvider
from api.schemas import User, UserCreate, UserUpdate
from api.utils.validators import check_only_one_parameter_not_none
from database.models import User as UserModel


async def read_users(db_provider: DatabaseProvider = Depends(DatabaseProvider)) -> list[User]:
    """Returns users from the database.

    Args:
        db_provider (DatabaseProvider): Provider for database.

    """
    query = select(UserModel)
    users = await db_provider.select(query, fetch_all=True)
    return [User.model_validate(user[0]) for user in users]


async def read_user(
    id: int | None = None, telegram_id: int | None = None, db_provider: DatabaseProvider = Depends(DatabaseProvider)
) -> User:
    """Returns user from the database.

    Args:
        id (int | None): Id of the user to get. Default is None.
        telegram_id (int | None): Telegram id of the user to get. Default is None.
        db_provider (DatabaseProvider): Provider for database.

    Raises:
        HTTPException (404): User not found.

    """
    check_only_one_parameter_not_none(id=id, telegram_id=telegram_id)

    query = select(UserModel).where((UserModel.id == id) if id is not None else (UserModel.telegram_id == telegram_id))
    if user := await db_provider.select(query, fetch_all=False):
        return User.model_validate(user[0])
    raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")


async def create_user(user: UserCreate, db_provider: DatabaseProvider = Depends(DatabaseProvider)) -> User:
    """Creates user in the database.

    Args:
        user (UserCreate): User to create.
        db_provider (DatabaseProvider): Provider for database.

    Returns:
        User: Created user.

    Raises:
        HTTPException (409): User with the given `telegram_id` already exists in database.

    """
    query = insert(UserModel).values(user.model_dump())
    user_id = await db_provider.insert(query)
    if user_id is not None:
        return await read_user(telegram_id=user.telegram_id, db_provider=db_provider)
    raise HTTPException(status.HTTP_409_CONFLICT, f"User with telegram id {user.telegram_id} already exists")


async def update_user(
    user: UserUpdate,
    id: int | None = None,
    telegram_id: int | None = None,
    db_provider: DatabaseProvider = Depends(DatabaseProvider),
) -> User:
    """Updates user in the database.

    Args:
        user (UserUpdate): User data to update.
        id (int | None): Id of the user to update. Default is None.
        telegram_id (int | None): Telegram id of the user to update. Default is None.
        db_provider (DatabaseProvider): Provider for database.

    Returns:
        User: Updated user.

    """
    check_only_one_parameter_not_none(id=id, telegram_id=telegram_id)

    query = (
        update(UserModel)
        .where((UserModel.id == id) if id is not None else (UserModel.telegram_id == telegram_id))
        .values(user.model_dump(exclude_none=True))
    )
    await db_provider.execute(query)
    return await read_user(telegram_id=telegram_id, db_provider=db_provider)


async def delete_user(
    id: int | None = None, telegram_id: int | None = None, db_provider: DatabaseProvider = Depends(DatabaseProvider)
) -> None:
    """Deletes user from the database.

    Args:
        id (int | None): Id of the user to delete. Default is None.
        telegram_id (int | None): Telegram id of the user to delete. Default is None.
        db_provider (DatabaseProvider): Provider for database.

    """
    check_only_one_parameter_not_none(id=id, telegram_id=telegram_id)
    query = delete(UserModel).where((UserModel.id == id) if id is not None else (UserModel.telegram_id == telegram_id))
    await db_provider.execute(query)


def setup(router: APIRouter) -> None:
    """Adds user routes for the FastAPI `router`."""
    router.add_api_route("/users/", read_users, methods=["GET"], response_model=list[User])
    router.add_api_route("/user/", read_user, methods=["GET"], response_model=User)
    router.add_api_route("/user/", create_user, methods=["POST"], response_model=User)
    router.add_api_route("/user/", update_user, methods=["PATCH"], response_model=User)
    router.add_api_route("/user/", delete_user, methods=["DELETE"], response_model=None)
