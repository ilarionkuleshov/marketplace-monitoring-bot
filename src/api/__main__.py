"""Script to run the API."""

import logging

import uvicorn
from fastapi import FastAPI

from api.routers import users_router
from settings import ApiSettings, GeneralSettings


def create_app() -> FastAPI:
    """Returns configured FastAPI application."""
    fastapi_app = FastAPI()
    fastapi_app.include_router(users_router)
    return fastapi_app


if __name__ == "__main__":
    logging.basicConfig(level=GeneralSettings().log_level)
    app = create_app()
    api_settings = ApiSettings()
    uvicorn.run(app, host=api_settings.host, port=api_settings.port)
