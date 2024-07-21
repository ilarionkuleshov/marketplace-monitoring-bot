from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresCredentials(BaseSettings):
    """Credentials for the postgres database."""

    host: str
    port: int
    user: str
    password: str
    database: str

    model_config = SettingsConfigDict(env_file=find_dotenv(), env_prefix="postgres_")

    def get_url(self) -> str:
        """Returns connection url for the postgres database."""
        template = "postgresql://{user}:{password}@{host}:{port}/{database}"
        return template.format(self.model_dump())
