import uvicorn
from fastapi import Depends, FastAPI

from api.dependencies import verify_api_key
from api.routers import (
    adverts_router,
    health_router,
    marketplaces_router,
    monitoring_runs_router,
    monitorings_router,
    users_router,
)
from settings import ApiSettings


def main() -> None:
    """Runs the FastAPI application."""
    app = FastAPI(dependencies=[Depends(verify_api_key)])
    app.include_router(health_router)
    app.include_router(marketplaces_router)
    app.include_router(users_router)
    app.include_router(monitorings_router)
    app.include_router(monitoring_runs_router)
    app.include_router(adverts_router)

    settings = ApiSettings()
    uvicorn.run(app, host=settings.host, port=settings.port, log_level=settings.log_level.lower())


if __name__ == "__main__":
    main()
