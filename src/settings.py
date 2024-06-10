from string import Template

from dotenv import find_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeneralSettings(BaseSettings):
    """General settings for the project."""

    log_level: str

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")


class PostgresCredentials(BaseSettings):
    """Credentials for the postgres database."""

    host: str
    port: int
    user: str
    password: str
    database: str

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore", env_prefix="postgres_")

    def get_url(self, use_async_driver: bool = True) -> str:
        """Returns connection url for the postgres database.

        Args:
            use_async_driver (bool): Whether to use async driver or sync. Default is True.

        """
        driver = "postgresql"
        if use_async_driver:
            driver += "+asyncpg"
        template = Template(f"{driver}://$user:$password@$host:$port/$database")
        return template.substitute(self.model_dump())


class ApiSettings(BaseSettings):
    """Settings for the api."""

    key: str = Field(min_length=40)
    host: str
    port: int

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore", env_prefix="api_")
