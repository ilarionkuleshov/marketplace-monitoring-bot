from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresCredentials(BaseSettings):
    """Credentials for the postgres database."""

    host: str
    port: int
    user: str
    password: str
    database: str

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore", env_prefix="postgres_")

    def get_url(self, use_sync_driver: bool = True) -> str:
        """Returns connection url for the postgres database.

        Args:
            use_sync_driver (bool): Whether to use sync driver. Default is True.

        """
        template = "{driver}://{user}:{password}@{host}:{port}/{database}"
        return template.format(
            driver="postgresql" if use_sync_driver else "postgresql+asyncpg",
            **self.model_dump(),
        )


class ApiConfig(BaseSettings):
    """Config for the API."""

    security_key: str

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore", env_prefix="api_")
