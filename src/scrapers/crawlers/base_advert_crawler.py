from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncIterator

from fastcrawl import BaseCrawler, CrawlerSettings, HttpClientSettings, LogSettings, Request, Response

from database.schemas import AdvertCreate
from scrapers.pipelines import (
    DebugSaveAdvertPipeline,
    FilterDuplicateAdvertPipeline,
    PublishAdvertPipeline,
)
from settings import ScrapersSettings


class BaseAdvertCrawler(BaseCrawler, ABC):
    """Base for all advert crawlers.

    Args:
        monitoring_id (int): Monitoring ID.
        monitoring_run_id (int): Monitoring run ID.
        monitoring_url (str): Monitoring URL to start scraping from.
        log_file (Path): Path to the log file.

    Attributes:
        See `Args` section.

    """

    monitoring_id: int
    monitoring_run_id: int
    monitoring_url: str

    def __init__(self, monitoring_id: int, monitoring_run_id: int, monitoring_url: str, log_file: Path) -> None:
        scrapers_settings = ScrapersSettings()
        crawler_settings = CrawlerSettings(
            workers=scrapers_settings.concurrency,
            pipelines=[FilterDuplicateAdvertPipeline],
            log=LogSettings(
                configure_globally=False,
                level=scrapers_settings.log_level,
                file=log_file,
                logger_name_suffix=str(monitoring_run_id),
            ),
            http_client=HttpClientSettings(headers={"User-Agent": scrapers_settings.user_agent}),
        )
        if scrapers_settings.debug_mode:
            crawler_settings.pipelines.append(DebugSaveAdvertPipeline)
        else:
            crawler_settings.pipelines.append(PublishAdvertPipeline)

        super().__init__(settings=crawler_settings)
        self.monitoring_id = monitoring_id
        self.monitoring_run_id = monitoring_run_id
        self.monitoring_url = monitoring_url

    async def generate_requests(self) -> AsyncIterator[Request]:
        """Yields a request to start scraping."""
        yield Request(url=self.monitoring_url, callback=self.parse_search_page)

    @abstractmethod
    async def parse_search_page(self, response: Response) -> AsyncIterator[AdvertCreate | Request]:
        """Parses search page.

        Args:
            response (Response): Search page response.

        Yields:
            AdvertCreate: Extracted advert.
            Request: Next page request.

        """

    @staticmethod
    def crop_str(str_value: str, max_length: int) -> str:
        """Returns cropped string.

        Args:
            str_value (str): String value.
            max_length (int): Maximum length of the string.

        """
        if len(str_value) > max_length:
            return str_value[: max_length - 3] + "..."
        return str_value
