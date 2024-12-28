FROM python:3.12.6-slim

ARG USERNAME=app
ARG UID=1000
ARG GID=1000
ARG WORKING_DIR=/marketplace-monitoring-bot
ARG POETRY_INSTALL_DEV=False

RUN groupadd --gid $GID $USERNAME \
    && useradd --uid $UID --gid $GID -m $USERNAME \
    && apt update \
    && apt install -y sudo python3-poetry \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

WORKDIR $WORKING_DIR
COPY pyproject.toml poetry.lock ./
COPY src ./src
COPY scripts ./scripts

RUN poetry env use python3.12

RUN if [ "$POETRY_INSTALL_DEV" = "False" ]; then poetry install --without dev; else poetry install; fi
