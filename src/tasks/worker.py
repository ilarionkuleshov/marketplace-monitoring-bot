import asyncio
import logging

from faststream import FastStream
from faststream.rabbit import RabbitBroker

from settings import TasksSettings


async def main() -> None:
    """Runs the FastStream application (worker)."""
    settings = TasksSettings()

    broker = RabbitBroker(settings.get_broker_url())
    app = FastStream(broker)

    await app.run(log_level=logging.getLevelName(settings.log_level))


if __name__ == "__main__":
    asyncio.run(main())
