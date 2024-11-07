from typing import Annotated

from faststream import Depends, Logger
from faststream.rabbit import RabbitRouter
from sqlalchemy import exists, func, not_, select
from sqlalchemy.sql import literal

from database import DatabaseProvider
from database.enums import MonitoringRunStatus
from database.models import Monitoring, MonitoringRun
from database.schemas import (
    MonitoringRead,
    MonitoringRunCreate,
    MonitoringRunRead,
    MonitoringRunUpdate,
)
from tasks.messages import ScrapingTask
from tasks.queues import SCRAPING_TASKS_QUEUE, TRIGGER_SCRAPING_TASKS_QUEUE

router = RabbitRouter()
scraping_task_publisher = router.publisher(SCRAPING_TASKS_QUEUE, persist=True)


@router.subscriber(TRIGGER_SCRAPING_TASKS_QUEUE)
async def handle_trigger_scraping_task(
    logger: Logger, database: Annotated[DatabaseProvider, Depends(DatabaseProvider)]
) -> None:
    """Handles trigger scraping task.

    Args:
        logger (Logger): FastStream logger.
        database (DatabaseProvider): Provider for the database.

    """
    monitorings = await database.get_all(
        model=Monitoring,
        read_schema=MonitoringRead,
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
            (
                select(func.max(MonitoringRun.created_at))
                .where(MonitoringRun.monitoring_id == Monitoring.id)
                .as_scalar()
                + Monitoring.run_interval
            )
            <= func.now(),  # pylint: disable=E1102
        ],
    )

    for monitoring in monitorings:
        await database.create(
            model=MonitoringRun,
            data=MonitoringRunCreate(monitoring_id=monitoring.id),
            read_schema=MonitoringRunRead,
        )

    monitoring_runs = await database.get_all(
        model=MonitoringRun,
        read_schema=MonitoringRunRead,
        filters=[MonitoringRun.status == MonitoringRunStatus.SCHEDULED],
    )
    logger.info(f"Publishing {len(monitoring_runs)} scraping tasks...")

    for monitoring_run in monitoring_runs:
        monitoring = await database.get(
            model=Monitoring, read_schema=MonitoringRead, filters=[Monitoring.id == monitoring_run.monitoring_id]
        )
        await scraping_task_publisher.publish(
            ScrapingTask(
                monitoring_id=monitoring.id, monitoring_url=monitoring.url, monitoring_run_id=monitoring_run.id
            )
        )
        await database.update(
            model=MonitoringRun,
            data=MonitoringRunUpdate(status=MonitoringRunStatus.QUEUED),
            filters=[MonitoringRun.id == monitoring_run.id],
            read_schema=MonitoringRunRead,
        )
