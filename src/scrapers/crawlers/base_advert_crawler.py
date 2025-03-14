from abc import ABC
from pathlib import Path

from fastcrawl import BaseCrawler, CrawlerSettings, HttpClientSettings, LogSettings

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

    def crop_advert_description(self, description: str | None) -> str | None:
        """Returns cropped advert description if it's not None.

        Args:
            description (str | None): Advert description.

        """
        if not description:
            return None
        return self.crop_str(description, 300)

    def crop_advert_title(self, title: str) -> str:
        """Returns cropped advert title.

        Args:
            title (str): Advert title.

        """
        return self.crop_str(title, 100)

    def crop_str(self, str_value: str, max_length: int) -> str:
        """Returns cropped string.

        Args:
            str_value (str): String value.
            max_length (int): Maximum length of the string.

        """
        if len(str_value) > max_length:
            return str_value[: max_length - 3] + "..."
        return str_value
