"""Routes for the interacting with search query entities."""

# pylint: disable=W0622

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from api.dependencies import DatabaseProvider
from api.routes.user import read_user
from api.schemas import SearchQuery, SearchQueryCreate, SearchQueryUpdate
from database.models import SearchQuery as SearchQueryModel
from database.models import User as UserModel


async def read_search_query(id: int, db_provider: DatabaseProvider = Depends(DatabaseProvider)) -> SearchQuery:
    """Returns search query from the database.

    Args:
        id (int): Id of the search query to get.
        db_provider (DatabaseProvider): Provider for database.

    Raises:
        HTTPException: Search query with the given `id` not found.

    """
    query = select(SearchQueryModel).where(UserModel.id == id)
    if search_query := await db_provider.select(query, fetch_all=False):
        return SearchQuery.model_validate(search_query[0])
    raise HTTPException(status.HTTP_404_NOT_FOUND, f"Search query with ID {id} not found")


async def read_search_queries(
    user_telegram_id: int, db_provider: DatabaseProvider = Depends(DatabaseProvider)
) -> list[SearchQuery]:
    """Returns list of search queries from the database.

    Args:
        user_telegram_id (int): Telegram id of the user for whom search queries will be retrieved.
        db_provider (DatabaseProvider): Provider for database.

    """
    query = (
        select(SearchQueryModel)
        .join(UserModel, UserModel.id == SearchQueryModel.user_id)
        .where(UserModel.telegram_id == user_telegram_id)
    )
    search_queries = await db_provider.select(query, fetch_all=True)
    return [SearchQuery.model_validate(search_query[0]) for search_query in search_queries]


async def create_search_query(
    search_query: SearchQueryCreate, db_provider: DatabaseProvider = Depends(DatabaseProvider)
) -> SearchQuery:
    """Creates search query in the database.

    Args:
        search_query (SearchQueryCreate): Search query to create.
        db_provider (DatabaseProvider): Provider for database.

    Returns:
        SearchQuery: Created search query.

    Raises:
        HTTPException: Search query with given url already exists for given user.

    """
    search_query_values = search_query.model_dump(exclude={"user_telegram_id"})
    search_query_values["user_id"] = (await read_user(search_query.user_telegram_id, db_provider)).id

    query = insert(SearchQueryModel).values(search_query_values).returning(SearchQueryModel.id)
    search_query_id = await db_provider.insert(query)
    if search_query_id is not None:
        return await read_search_query(search_query_id, db_provider)

    raise HTTPException(
        status.HTTP_409_CONFLICT,
        f"Search query with url {search_query.url} for user {search_query.user_telegram_id} already exists",
    )


async def update_search_query(
    id: int, search_query: SearchQueryUpdate, db_provider: DatabaseProvider = Depends(DatabaseProvider)
) -> SearchQuery:
    """Updates search query in the database.

    Args:
        id (int): Id of the search query to update.
        search_query (SearchQueryUpdate): Search query data to update.
        db_provider (DatabaseProvider): Provider for database.

    Returns:
        SearchQuery: Updated search query.

    """
    query = update(SearchQueryModel).where(SearchQueryModel.id == id).values(search_query.model_dump(exclude_none=True))
    await db_provider.execute(query)
    return await read_search_query(id=id, db_provider=db_provider)


async def delete_search_query(id: int, db_provider: DatabaseProvider = Depends(DatabaseProvider)) -> None:
    """Deletes search query from the database.

    Args:
        id (int): Id of the search query to delete.
        db_provider (DatabaseProvider): Provider for database.

    """
    query = delete(SearchQueryModel).where(SearchQueryModel.id == id)
    await db_provider.execute(query)


def setup(router: APIRouter) -> None:
    """Adds user routes for the FastAPI `router`."""
    router.add_api_route("/search_query/", read_search_query, methods=["GET"], response_model=SearchQuery)
    router.add_api_route("/search_queries/", read_search_queries, methods=["GET"], response_model=list[SearchQuery])
    router.add_api_route("/search_query/", create_search_query, methods=["POST"], response_model=SearchQuery)
    router.add_api_route("/search_query/", update_search_query, methods=["PATCH"], response_model=SearchQuery)
    router.add_api_route("/search_query/", delete_search_query, methods=["DELETE"], response_model=None)
