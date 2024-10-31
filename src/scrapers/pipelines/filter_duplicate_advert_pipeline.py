from typing import Any

from scrapy import Spider
from scrapy.exceptions import DropItem

from database.schemas import AdvertCreate


# pylint: disable=W0613
class FilterDuplicateAdvertPipeline:
    """Pipeline to filter duplicate adverts.

    Attributes:
        unique_advert_urls (set[str]): A set to store unique advert urls.

    """

    unique_advert_urls: set[str]

    def __init__(self) -> None:
        self.unique_advert_urls = set()

    def process_item(self, item: Any, spider: Spider) -> Any:
        """Filters duplicate adverts based on the advert's url."""
        if not isinstance(item, AdvertCreate):
            return item

        advert_url = str(item.url)
        if advert_url in self.unique_advert_urls:
            raise DropItem(f"Duplicate advert found: {advert_url}")

        self.unique_advert_urls.add(advert_url)
        return item
