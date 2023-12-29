"""Utilities for FastAPI app."""

from fastapi import Depends, FastAPI

from api import routes
from api.dependencies import validate_api_key


def create_app() -> FastAPI:
    """Returns configured FastAPI application."""
    app = FastAPI(dependencies=[Depends(validate_api_key)])
    routes.setup(app.router)
    return app
