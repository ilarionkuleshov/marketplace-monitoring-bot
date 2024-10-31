from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured

from database.schemas import AdvertCreate
from settings import ScrapersSettings


# pylint: disable=W0613
class DebugSaveAdvertPipeline:
    """Pipeline to save adverts locally for debugging purposes.

    Args:
        spider_name (str): The name of the spider.

    Attributes:
        storage_path (Path): The path to save the adverts.

    """

    storage_path: Path

    def __init__(self, spider_name: str) -> None:
        current_datetime = datetime.now().replace(microsecond=0)
        self.storage_path = (
            Path("./storage/adverts/")
            / spider_name
            / current_datetime.date().isoformat()
            / current_datetime.time().isoformat()
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> DebugSaveAdvertPipeline:
        """Returns an instance of the pipeline if debug mode is enabled."""
        if not ScrapersSettings().debug_mode:
            raise NotConfigured
        return cls(spider_name=crawler.spidercls.name)

    def process_item(self, item: Any, spider: Spider) -> Any:
        """Saves the advert to a file."""
        if not isinstance(item, AdvertCreate):
            return item

        advert_id = hashlib.md5(str(item.url).encode()).hexdigest()
        advert_path = self.storage_path / f"{advert_id}.json"
        advert_path.write_text(item.model_dump_json(indent=4), encoding="utf-8")

        return item
