import traceback
from datetime import datetime
from pathlib import Path

from faststream import Logger
from faststream.rabbit import RabbitRouter
from sqlalchemy import select

from bot.utils.adverts import send_advert_message
from database import get_database
from database.enums import MonitoringRunStatus
from database.models import Advert, Monitoring, MonitoringRun, User
from database.schemas import (
    AdvertCreate,
    AdvertRead,
    AdvertUpdate,
    MonitoringRunRead,
    MonitoringRunUpdate,
    UserRead,
)
from scrapers.crawlers import BaseAdvertCrawler, OlxUaCrawler
from tasks.messages import ScrapingTask
from tasks.queues import SCRAPING_RESULTS_QUEUE, SCRAPING_TASKS_QUEUE

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

    log_file_dir = Path("./storage/logs/")
    log_file_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_file_dir / f"{scraping_task.monitoring_run_id}.log"

    crawler_cls: type[BaseAdvertCrawler] = {"Olx UA": OlxUaCrawler}[scraping_task.marketplace_name]
    crawler = crawler_cls(
        monitoring_id=scraping_task.monitoring_id,
        monitoring_run_id=scraping_task.monitoring_run_id,
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
                log_file=str(log_file),
                duration=datetime.now() - start_time,
                status=status,
            ),
            filters=[MonitoringRun.id == scraping_task.monitoring_run_id],
        )


@router.subscriber(SCRAPING_RESULTS_QUEUE)
async def process_scraping_result(scraped_advert: AdvertCreate, logger: Logger) -> None:
    """Processes scraping result.

    Args:
        scraped_advert (AdvertCreate): Scraped advert.
        logger (Logger): FastStream logger.

    """
    async with get_database() as database:
        advert = await database.create(
            model=Advert, data=scraped_advert, update_on_conflict=True, read_schema=AdvertRead
        )
        first_monitoring_run = await database.get(
            model=MonitoringRun,
            filters=[MonitoringRun.monitoring_id == advert.monitoring_id],
            order_by=[MonitoringRun.created_at.asc()],
            read_schema=MonitoringRunRead,
        )

    if not first_monitoring_run:
        logger.error(f"Monitoring run for advert {advert.id} not found")
        return

    if advert.monitoring_run_id != first_monitoring_run.id and not advert.sent_to_user:
        async with get_database() as database:
            user = await database.get_by_query(
                query=select(User)
                .join(Monitoring, Monitoring.user_id == User.id)
                .where(Monitoring.id == advert.monitoring_id),
                by_mappings=False,
                read_schema=UserRead,
            )
        if user is None:
            logger.error(f"User for advert {advert.id} not found")
            return
        logger.info(f"Sending advert {advert.id} to user")
        await send_advert_message(advert, user)

    async with get_database() as database:
        await database.update(
            model=Advert,
            data=AdvertUpdate(sent_to_user=True),
            filters=[Advert.id == advert.id],
        )
