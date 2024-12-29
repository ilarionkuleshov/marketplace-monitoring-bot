import traceback
from datetime import datetime
from pathlib import Path

from faststream import Logger
from faststream.rabbit import RabbitRouter

from database import get_database
from database.enums import MonitoringRunStatus
from database.models import MonitoringRun
from database.schemas import MonitoringRunUpdate
from scrapers.crawlers import BaseAdvertCrawler, OlxUaCrawler
from tasks.messages import ScrapingTask
from tasks.queues import SCRAPING_TASKS_QUEUE

router = RabbitRouter()


@router.subscriber(SCRAPING_TASKS_QUEUE)
async def process_scraping_task(scraping_task: ScrapingTask, logger: Logger) -> None:
    """Processes scraping task.

    Args:
        scraping_task (ScrapingTask): Scraping task to process.
        logger (Logger): FastStream logger.

    """
    async with get_database() as database:
        await database.update(
            model=MonitoringRun,
            data=MonitoringRunUpdate(status=MonitoringRunStatus.RUNNING),
            filters=[MonitoringRun.id == scraping_task.monitoring_run_id],
        )

    log_file = Path("./storage/logs/") / f"{scraping_task.monitoring_run_id}.log"
    log_file.mkdir(parents=True, exist_ok=True)

    crawler_cls: type[BaseAdvertCrawler] = {"Olx UA": OlxUaCrawler}[scraping_task.marketplace_name]
    crawler = crawler_cls(
        monitoring_id=scraping_task.monitoring_id,
        monitoring_url=scraping_task.monitoring_url,
        log_file=log_file,
    )

    start_time = datetime.now()
    try:
        await crawler.run()
        status = MonitoringRunStatus.SUCCESS
    except Exception:  # pylint: disable=W0718
        logger.error(f"Error occurred during scraping: {traceback.format_exc()}")
        status = MonitoringRunStatus.FAILED

    async with get_database() as database:
        await database.update(
            model=MonitoringRun,
            data=MonitoringRunUpdate(
                log_file=log_file,
                duration=datetime.now() - start_time,
                status=status,
            ),
            filters=[MonitoringRun.id == scraping_task.monitoring_run_id],
        )
