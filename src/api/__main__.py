import logging

import uvicorn
from fastapi import FastAPI, Security

from api.dependencies import verify_api_key
from api.routers import users_router

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    app = FastAPI(dependencies=[Security(verify_api_key)])
    app.include_router(users_router)

    uvicorn.run(app)
