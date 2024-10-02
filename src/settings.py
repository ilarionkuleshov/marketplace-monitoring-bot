from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresCredentials(BaseSettings):
    """Credentials for connecting to a PostgreSQL database."""

    host: str
    port: int
    user: str
    password: str
    database: str

    model_config = SettingsConfigDict(env_prefix="postgres_", env_file=find_dotenv(), extra="ignore")

    def get_url(self, async_driver: bool = True) -> str:
        """Returns the connection URL for the database.

        Args:
            async_driver (bool): Whether to use an async driver.

        """
        driver = "postgresql+asyncpg" if async_driver else "postgresql"
        return f"{driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
