ARG PYTHON_IMAGE

FROM ${PYTHON_IMAGE}

RUN apk --no-cache add git gcc musl-dev
RUN pip install poetry

WORKDIR /app
COPY .env pyproject.toml poetry.lock ./
COPY src ./src
COPY tests ./tests

RUN poetry install
