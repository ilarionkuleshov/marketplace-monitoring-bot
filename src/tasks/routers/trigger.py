import asyncio

from faststream import Logger
from faststream.rabbit import RabbitRouter
from sqlalchemy import exists, func, not_, or_, select
from sqlalchemy.sql import literal

from database import get_database
from database.enums import MonitoringRunStatus
from database.models import Monitoring, MonitoringRun
from database.schemas import MonitoringRead, MonitoringRunCreate, MonitoringRunUpdate
from tasks.messages import ScrapingTask
from tasks.queues import SCRAPING_TASKS_QUEUE, TRIGGER_SCRAPING_TASKS_QUEUE

router = RabbitRouter()
scraping_task_publisher = router.publisher(SCRAPING_TASKS_QUEUE, persist=True)
lock = asyncio.Lock()


@router.subscriber(TRIGGER_SCRAPING_TASKS_QUEUE)
async def handle_trigger_scraping_task(logger: Logger) -> None:
    """Handles trigger scraping task.

    Args:
        logger (Logger): FastStream logger.

    """
    async with lock:
        async with get_database() as database:
            monitorings = await database.get_all(
                model=Monitoring,
                filters=[
                    Monitoring.enabled.is_(True),
                    not_(
                        exists(
                            select(literal(1)).where(
                                MonitoringRun.monitoring_id == Monitoring.id,
                                MonitoringRun.status.notin_([MonitoringRunStatus.SUCCESS, MonitoringRunStatus.FAILED]),
                            )
                        )
                    ),
                    or_(
                        not_(exists(select(literal(1)).where(MonitoringRun.monitoring_id == Monitoring.id))),
                        (
                            select(func.max(MonitoringRun.created_at))
                            .where(MonitoringRun.monitoring_id == Monitoring.id)
                            .as_scalar()
                            + Monitoring.run_interval
                        )
                        <= func.now(),  # pylint: disable=E1102
                    ),
                ],
                read_schema=MonitoringRead,
            )

            for monitoring in monitorings:
                await database.create(
                    model=MonitoringRun,
                    data=MonitoringRunCreate(monitoring_id=monitoring.id),
                )

            scraping_tasks = await database.get_all_by_query(
                query=select(
                    Monitoring.id.label("monitoring_id"),
                    Monitoring.url.label("monitoring_url"),
                    MonitoringRun.id.label("monitoring_run_id"),
                )
                .join(MonitoringRun, MonitoringRun.monitoring_id == Monitoring.id)
                .where(MonitoringRun.status == MonitoringRunStatus.SCHEDULED),
                read_schema=ScrapingTask,
            )

            for scraping_task in scraping_tasks:
                await database.update(
                    model=MonitoringRun,
                    data=MonitoringRunUpdate(status=MonitoringRunStatus.QUEUED),
                    filters=[MonitoringRun.id == scraping_task.monitoring_run_id],
                )

        for scraping_task in scraping_tasks:
            await scraping_task_publisher.publish(scraping_task)

        logger.info(f"Published {len(scraping_tasks)} scraping tasks")
