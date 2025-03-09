from fastcrawl import BasePipeline

from database.schemas import AdvertCreate


class FilterDuplicateAdvertPipeline(BasePipeline):
    """Pipeline to filter duplicate adverts.

    Attributes:
        unique_advert_urls (set[str]): A set to store unique advert urls.

    """

    allowed_items = [AdvertCreate]

    unique_advert_urls: set[str]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.unique_advert_urls = set()

    async def process_item(self, item: AdvertCreate) -> AdvertCreate | None:
        """Filters duplicate adverts based on the advert's url.

        Args:
            item (AdvertCreate): The advert to filter.

        Returns:
            AdvertCreate: The advert if it is not a duplicate.
            None: If the advert is a duplicate.

        """
        advert_url = str(item.url)
        if advert_url in self.unique_advert_urls:
            return None

        self.unique_advert_urls.add(advert_url)
        return item
