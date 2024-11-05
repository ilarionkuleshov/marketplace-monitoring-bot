import argparse
import asyncio
import logging

from faststream import FastStream
from faststream.rabbit import RabbitBroker
from taskiq.cli.scheduler.run import SchedulerArgs
from taskiq.cli.scheduler.run import run_scheduler as run_scheduler_
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_faststream import BrokerWrapper, StreamScheduler

from settings import TasksSettings
from tasks.queues import MONITORING_CHECK_TASKS_QUEUE
from tasks.routers import monitoring_router, scraping_router


async def get_broker(settings: TasksSettings) -> RabbitBroker:
    """Returns a RabbitMQ broker instance."""
    return RabbitBroker(settings.get_broker_url())


async def run_worker(settings: TasksSettings) -> None:
    """Runs the FastStream worker."""
    broker = await get_broker(settings)
    broker.include_router(monitoring_router)
    broker.include_router(scraping_router)

    app = FastStream(broker)
    await app.run(log_level=logging.getLevelName(settings.log_level))


async def run_scheduler(settings: TasksSettings) -> None:
    """Runs the FastStream scheduler."""
    broker = await get_broker(settings)

    taskiq_broker = BrokerWrapper(broker)
    taskiq_broker.task(
        queue=MONITORING_CHECK_TASKS_QUEUE,
        schedule=[{"cron": "* * * * *"}],
    )

    scheduler = StreamScheduler(
        broker=taskiq_broker,
        sources=[LabelScheduleSource(taskiq_broker)],
    )
    await run_scheduler_(
        SchedulerArgs(
            scheduler=scheduler,
            log_level=settings.log_level,
            modules=[],
        ),
    )


async def main() -> None:
    """Runs the FastStream application."""
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        dest="app_type",
        choices=["worker", "scheduler"],
        help="The type of FastStream application to run.",
    )
    args = arg_parser.parse_args()

    settings = TasksSettings()
    if args.app_type == "worker":
        await run_worker(settings)
    else:
        await run_scheduler(settings)


if __name__ == "__main__":
    asyncio.run(main())
