import uvicorn
from fastapi import FastAPI

from api.routers import health_router
from settings import ApiSettings


def main() -> None:
    """Runs the FastAPI application."""
    app = FastAPI()
    app.include_router(health_router)

    settings = ApiSettings()
    uvicorn.run(app, host=settings.host, port=settings.port, log_level=settings.log_level)


if __name__ == "__main__":
    main()
