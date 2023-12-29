from fastapi import APIRouter

from . import user


def setup(router: APIRouter) -> None:
    """Adds all routes for the FastAPI `router`."""
    user.setup(router)
