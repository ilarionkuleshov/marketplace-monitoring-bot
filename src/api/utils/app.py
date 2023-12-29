"""Utilities for FastAPI app."""

from fastapi import FastAPI

from api import routes


def create_app() -> FastAPI:
    """Returns configured FastAPI application."""
    app = FastAPI()
    routes.setup(app.router)
    return app
