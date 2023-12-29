"""Script to start the API.

Command to run (in `src` directory):
    $ python -m api

"""

import uvicorn

from api.utils import create_app
from settings import api_settings
from utils.log import configure_logging

if __name__ == "__main__":
    configure_logging()
    app = create_app()
    config = api_settings()
    uvicorn.run(app, host=str(config.API_HOST_TO_RUN), port=config.API_PORT)
