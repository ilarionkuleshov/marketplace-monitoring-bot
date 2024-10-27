import uvicorn
from fastapi import Depends, FastAPI

from api.dependencies import verify_api_key
from api.routers import health_router, marketplaces_router
from settings import ApiSettings


def main() -> None:
    """Runs the FastAPI application."""
    app = FastAPI(dependencies=[Depends(verify_api_key)])
    app.include_router(health_router)
    app.include_router(marketplaces_router)

    settings = ApiSettings()
    uvicorn.run(app, host=settings.host, port=settings.port, log_level=settings.log_level)


if __name__ == "__main__":
    main()
