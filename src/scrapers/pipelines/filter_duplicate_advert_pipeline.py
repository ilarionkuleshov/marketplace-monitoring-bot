from fastcrawl import BasePipeline

from database.schemas import AdvertCreate


class FilterDuplicateAdvertPipeline(BasePipeline[AdvertCreate]):
    """Pipeline to filter duplicate adverts.

    Attributes:
        unique_advert_urls (set[str]): A set to store unique advert urls.
        **kwargs: Keyword arguments to pass to the parent class.

    """

    unique_advert_urls: set[str]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.unique_advert_urls = set()

    async def process_item(self, item: AdvertCreate) -> AdvertCreate | None:
        """Filters duplicate adverts based on the advert's url.

        Args:
            item (AdvertCreate): The advert to filter.

        Returns:
            AdvertCreate: The advert if it is not a duplicate.
            None: If the advert is a duplicate.

        """
        if not isinstance(item, AdvertCreate):
            return item

        advert_url = str(item.url)
        if advert_url in self.unique_advert_urls:
            return None

        self.unique_advert_urls.add(advert_url)
        return item
