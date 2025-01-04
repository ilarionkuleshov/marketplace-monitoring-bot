import traceback
from datetime import datetime
from pathlib import Path

from aiogram import Bot
from faststream import Logger
from faststream.rabbit import RabbitRouter

from database import get_database
from database.enums import MonitoringRunStatus
from database.models import Advert, Monitoring, MonitoringRun
from database.schemas import (
    AdvertCreate,
    AdvertRead,
    AdvertUpdate,
    MonitoringRead,
    MonitoringRunRead,
    MonitoringRunUpdate,
)
from scrapers.crawlers import BaseAdvertCrawler, OlxUaCrawler
from settings import BotSettings
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
        logger.info(f"Sending advert {advert.id} to user")
        async with get_database() as database:
            monitoring = await database.get(
                model=Monitoring, filters=[Monitoring.id == advert.monitoring_id], read_schema=MonitoringRead
            )
        if monitoring:
            bot = Bot(BotSettings().token)
            if advert.image:
                await bot.send_photo(
                    chat_id=monitoring.user_id,
                    photo=advert.image,
                    caption=advert.get_telegram_message(),
                    parse_mode="HTML",
                )
            else:
                await bot.send_message(
                    chat_id=monitoring.user_id, text=advert.get_telegram_message(), parse_mode="HTML"
                )

    async with get_database() as database:
        await database.update(
            model=Advert,
            data=AdvertUpdate(sent_to_user=True),
            filters=[Advert.id == advert.id],
        )
