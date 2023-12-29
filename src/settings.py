"""Project settings that are loaded from `.env` file."""

from functools import lru_cache
from ipaddress import IPv4Address
from string import Template
from typing import Literal

from dotenv import find_dotenv
from furl import furl
from pydantic import UUID4, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeneralSettings(BaseSettings):
    """General project settings."""

    LOG_LEVEL: Literal["NOTSET", "DEBUG", "INFO", "WARNING", "WARN", "ERROR", "FATAL", "CRITICAL"]

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")


class DBCredentials(BaseSettings):
    """Credentials for the database."""

    DB_HOST: IPv4Address | Literal["localhost", "postgres"]
    DB_PORT: int
    DB_USERNAME: str = Field(..., min_length=1)
    DB_PASSWORD: str = Field(..., min_length=1)
    DB_NAME: str = Field(..., min_length=1)

    url_format: str = "$DRIVER://$DB_USERNAME:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    sync_driver: str = "postgresql"
    async_driver: str = "postgresql+asyncpg"

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")

    def build_url(self, use_sync_driver: bool = True) -> str:
        """Returns url to connect to the database.

        Args:
            use_sync_driver (bool): Whether to use synchronous driver or not. Default is `True`.

        """
        url_template = Template(self.url_format)
        url_mapping = self.model_dump()
        url_mapping["DRIVER"] = self.sync_driver if use_sync_driver else self.async_driver
        return url_template.substitute(url_mapping)


class AMQPCredentials(BaseSettings):
    """Credentials for the AMQP broker."""

    AMQP_HOST: IPv4Address | Literal["localhost", "rabbitmq"]
    AMQP_PORT: int
    AMQP_USERNAME: str = Field(..., min_length=1)
    AMQP_PASSWORD: str = Field(..., min_length=1)
    AMQP_VIRTUAL_HOST: str = Field(..., min_length=1)
    AMQP_SEARCH_TASK_QUEUE: str = Field(..., min_length=1)
    AMQP_SEARCH_RESULT_QUEUE: str = Field(..., min_length=1)
    AMQP_SEARCH_REPLY_QUEUE: str = Field(..., min_length=1)

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")


class APISettings(BaseSettings):
    """Settings for the API."""

    API_HOST_TO_RUN: IPv4Address
    API_HOST_TO_CONNECT: IPv4Address | Literal["api"]
    API_PORT: int
    API_KEY: UUID4

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")

    def build_url(self, path: str = "") -> str:
        """Returns url to connect to the API."""
        return furl(scheme="http", host=str(self.API_HOST_TO_CONNECT), port=self.API_PORT, path=path).url


@lru_cache
def general_settings() -> GeneralSettings:
    """Returns the general project settings."""
    return GeneralSettings()


@lru_cache
def db_credentials() -> DBCredentials:
    """Returns the credentials for the database."""
    return DBCredentials()


@lru_cache
def amqp_credentials() -> AMQPCredentials:
    """Returns the credentials for the AMQP broker."""
    return AMQPCredentials()


@lru_cache
def api_settings() -> APISettings:
    """Returns settings for the API."""
    return APISettings()
