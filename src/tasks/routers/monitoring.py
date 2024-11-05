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
from tasks.queues import MONITORING_CHECK_TASKS_QUEUE, SCRAPING_TASKS_QUEUE

router = RabbitRouter()


@router.subscriber(MONITORING_CHECK_TASKS_QUEUE)
@router.publisher(SCRAPING_TASKS_QUEUE)
async def handle_monitoring_check_task(
    logger: Logger, database: Annotated[DatabaseProvider, Depends(DatabaseProvider)]
) -> list[ScrapingTask]:
    """Handles monitoring check task.

    Args:
        logger (Logger): FastStream logger.
        database (DatabaseProvider): Provider for the database.

    Returns:
        list[ScrapingTask]: Initiated scraping tasks.

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
    logger.info(f"Found {len(monitorings)} monitorings to create runs for")

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
    logger.info(f"Found {len(monitoring_runs)} scheduled monitoring runs")

    scraping_tasks = []

    for monitoring_run in monitoring_runs:
        await database.update(
            model=MonitoringRun,
            data=MonitoringRunUpdate(status=MonitoringRunStatus.QUEUED),
            filters=[MonitoringRun.id == monitoring_run.id],
            read_schema=MonitoringRunRead,
        )
        monitoring = await database.get(
            model=Monitoring, read_schema=MonitoringRead, filters=[Monitoring.id == monitoring_run.monitoring_id]
        )
        scraping_tasks.append(
            ScrapingTask(
                monitoring_id=monitoring.id, monitoring_url=monitoring.url, monitoring_run_id=monitoring_run.id
            )
        )

    logger.info(f"Returning {len(scraping_tasks)} scraping tasks")
    return scraping_tasks
