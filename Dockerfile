FROM python:3.12.3-slim

ARG USERNAME=bot
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt update \
    && apt install -y sudo python3-poetry \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

WORKDIR /marketplace-monitoring-bot
COPY pyproject.toml poetry.lock ./
COPY src ./src
COPY tests ./tests
COPY scripts ./scripts

RUN poetry env use python3.12 && poetry install
