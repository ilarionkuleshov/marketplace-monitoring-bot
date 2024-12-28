from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Settings for the PostgreSQL database."""

    host: str
    port: int
    user: str
    password: str
    name: str

    model_config = SettingsConfigDict(env_prefix="database_", env_file=find_dotenv(), extra="ignore")

    def get_url(self, async_driver: bool = True) -> str:
        """Returns the connection URL for the PostgreSQL database.

        Args:
            async_driver (bool): Whether to use an async driver.

        """
        driver = "postgresql+asyncpg" if async_driver else "postgresql"
        return f"{driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class ApiSettings(BaseSettings):
    """Settings for the FastAPI application."""

    log_level: str
    host: str
    port: int
    security_key: str

    model_config = SettingsConfigDict(env_prefix="api_", env_file=find_dotenv(), extra="ignore")


class ScrapersSettings(BaseSettings):
    """Settings for the FastCrawl scrapers."""

    log_level: str
    user_agent: str
    concurrency: int
    debug_mode: bool

    model_config = SettingsConfigDict(env_prefix="scrapers_", env_file=find_dotenv(), extra="ignore")


class TasksSettings(BaseSettings):
    """Settings for the FastStream background tasks."""

    log_level: str
    broker_host: str
    broker_port: int
    broker_management_port: int
    broker_user: str
    broker_password: str
    broker_vhost: str

    model_config = SettingsConfigDict(env_prefix="tasks_", env_file=find_dotenv(), extra="ignore")

    def get_broker_url(self) -> str:
        """Returns the connection URL for the RabbitMQ broker."""
        return (
            f"amqp://{self.broker_user}:{self.broker_password}"
            f"@{self.broker_host}:{self.broker_port}/{self.broker_vhost}"
        )
