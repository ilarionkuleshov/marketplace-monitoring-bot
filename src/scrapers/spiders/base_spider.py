from abc import ABC
from typing import Any

from scrapy import Spider
from scrapy.http import Response

from scrapers.pipelines import DebugSaveAdvertPipeline, FilterDuplicateAdvertPipeline


class BaseSpider(Spider, ABC):
    """Base for all spiders.

    Args:
        monitoring_id (int): Monitoring ID.
        monitoring_url (str): Monitoring URL to start scraping from.
        kwargs (dict[str, Any]): Additional keyword arguments.

    Attributes:
        See `Args` section.

    """

    custom_settings: dict | None = {
        "ITEM_PIPELINES": {
            FilterDuplicateAdvertPipeline: 400,
            DebugSaveAdvertPipeline: 500,
        },
    }

    monitoring_id: int
    monitoring_url: str

    def __init__(self, monitoring_id: int, monitoring_url: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.monitoring_id = monitoring_id
        self.monitoring_url = monitoring_url

    def parse(self, response: Response, **kwargs: Any) -> Any:
        """Just a stub."""
