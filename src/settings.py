from string import Template

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresCredentials(BaseSettings):
    """Credentials for the postgres database."""

    host: str
    port: int
    user: str
    password: str
    database: str

    model_config = SettingsConfigDict(env_prefix="postgres_", str_to_lower=True)

    def get_url(self) -> str:
        """Returns connection url for the postgres database."""
        template = Template("postgresql://$user:$password@$host:$port/$database")
        return template.substitute(self.model_dump())


class ApiSettings(BaseSettings):
    """Settings for the api."""

    key: str = Field(min_length=40)

    model_config = SettingsConfigDict(env_prefix="api_", str_to_lower=True)
