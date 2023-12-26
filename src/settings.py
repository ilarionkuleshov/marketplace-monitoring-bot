"""Project settings that are loaded from `.env` file."""

from functools import lru_cache
from ipaddress import IPv4Address
from typing import Literal

from pydantic import Field
from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBCredentials(BaseSettings):
    """Credentials for the database."""

    DB_HOST: IPv4Address | Literal["localhost", "postgres"]
    DB_PORT: int
    DB_USERNAME: str = Field(..., min_length=1)
    DB_PASSWORD: str = Field(..., min_length=1)
    DB_NAME: str = Field(..., min_length=1)

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")


class AMQPCredentials(BaseSettings):
    """Credentials for the AMQP broker."""

    AMQP_HOST: IPv4Address | Literal["localhost", "rabbitmq"]
    AMQP_PORT: int
    AMQP_USERNAME: str = Field(..., min_length=1)
    AMQP_PASSWORD: str = Field(..., min_length=1)
    AMQP_VIRTUAL_HOST: str = Field(..., min_length=1)
    AMQP_COLLECTION_TASK_QUEUE: str = Field(..., min_length=1)
    AMQP_COLLECTION_RESULT_QUEUE: str = Field(..., min_length=1)
    AMQP_COLLECTION_REPLY_QUEUE: str = Field(..., min_length=1)

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")


@lru_cache
def database_credentials() -> DBCredentials:
    """Returns the credentials for the database."""
    return DBCredentials()


@lru_cache
def amqp_credentials() -> AMQPCredentials:
    """Returns the credentials for the AMQP broker."""
    return AMQPCredentials()
