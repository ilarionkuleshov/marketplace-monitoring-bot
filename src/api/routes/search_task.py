"""Routes for the interacting with search task entities."""

# pylint: disable=W0622

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from api.dependencies import DatabaseProvider
from api.schemas import SearchTask, SearchTaskCreate
from database.models import SearchTask as SearchTaskModel


async def read_search_tasks(
    search_query_id: int | None = None, db_provider: DatabaseProvider = Depends(DatabaseProvider)
) -> list[SearchTask]:
    """Returns search tasks from the database.

    Args:
        search_query_id (int | None): Id of the search query for which search tasks will be retrieved. Default is None.
        db_provider (DatabaseProvider): Provider for database.

    """
    query = select(SearchTaskModel)
    if search_query_id is not None:
        query = query.where(SearchTaskModel.search_query_id == search_query_id)

    search_tasks = await db_provider.select(query, fetch_all=True)
    return [SearchTask.model_validate(search_task[0]) for search_task in search_tasks]


async def read_search_task(id: int, db_provider: DatabaseProvider = Depends(DatabaseProvider)) -> SearchTask:
    """Returns search task from the database.

    Args:
        id (int): Id of the search task to get.
        db_provider (DatabaseProvider): Provider for database.

    Raises:
        HTTPException (404): Search task not found.

    """
    query = select(SearchTaskModel).where(SearchTaskModel.id == id)
    if search_task := await db_provider.select(query, fetch_all=False):
        return SearchTask.model_validate(search_task[0])
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Search task not found")


async def create_search_task(
    search_task: SearchTaskCreate, db_provider: DatabaseProvider = Depends(DatabaseProvider)
) -> SearchTask:
    """Creates search task in the database.

    Args:
        search_task (SearchTaskCreate): Search task to create.
        db_provider (DatabaseProvider): Provider for database.

    Returns:
        SearchTask: Created search task.

    Raises:
        HTTPException (500): Unknown error occurred.

    """
    query = insert(SearchTaskModel).values(search_task.model_dump())
    search_task_id = await db_provider.insert(query)
    if search_task_id is not None:
        return await read_search_task(id=search_task_id, db_provider=db_provider)
    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Unknown error occurred")


def setup(router: APIRouter) -> None:
    """Adds user routes for the FastAPI `router`."""
    router.add_api_route("/search_tasks/", read_search_tasks, methods=["GET"], response_model=list[SearchTask])
    router.add_api_route("/search_task/", read_search_task, methods=["GET"], response_model=SearchTask)
    router.add_api_route("/search_task/", create_search_task, methods=["POST"], response_model=SearchTask)
