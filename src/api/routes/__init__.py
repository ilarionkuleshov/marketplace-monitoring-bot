from fastapi import APIRouter

from . import search_query, search_task, user


def setup(router: APIRouter) -> None:
    """Adds all routes for the FastAPI `router`."""
    user.setup(router)
    search_query.setup(router)
    search_task.setup(router)
