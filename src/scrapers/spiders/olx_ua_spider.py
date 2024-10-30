import json
from typing import Any, Iterator

from scrapy import Request, Spider
from scrapy.http import HtmlResponse, Response

from database.schemas import AdvertCreate
from scrapers.utils import crop_str


class OlxUaSpider(Spider):
    """Spider for scraping `olx.ua`.

    Args:
        monitoring_id (int): Monitoring ID.
        monitoring_url (str): Monitoring URL to start scraping from.

    Attributes:
        See `Args` section.

    """

    name: str = "olx_ua"

    monitoring_id: int
    monitoring_url: str

    def __init__(self, monitoring_id: int, monitoring_url: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.monitoring_id = monitoring_id
        self.monitoring_url = monitoring_url

    def start_requests(self) -> Iterator[Request]:
        """Yields a request to start scraping."""
        yield Request(url=self.monitoring_url, callback=self.parse_search_page)

    def parse_search_page(self, response: HtmlResponse) -> Iterator[AdvertCreate | Request]:
        """Parses search page.

        Args:
            response (HtmlResponse): HTML page response.

        Yields:
            AdvertCreate: Parsed advert.
            Request: Next page request.

        """
        raw_adverts = self._get_raw_adverts(response)

        for raw_advert in raw_adverts:
            if "url" not in raw_advert or "title" not in raw_advert:
                self.logger.warning(f"Skipping advert, missing required data: {raw_advert}")
                continue

            price_data = (raw_advert.get("price") or {}).get("regularPrice") or {}
            yield AdvertCreate(
                monitoring_id=self.monitoring_id,
                url=raw_advert["url"],
                title=crop_str(raw_advert["title"], 100),
                description=crop_str(raw_advert["description"], 300) if raw_advert.get("description") else None,
                image=raw_advert["photos"][0] if raw_advert.get("photos") else None,
                price=price_data.get("value") or None,
                currency=price_data.get("currencyCode") or None,
            )

        if next_page_url := response.xpath(".//a[@data-cy='pagination-forward']/@href").get():
            yield Request(url=response.urljoin(next_page_url), callback=self.parse_search_page)

    def _get_raw_adverts(self, response: HtmlResponse) -> list[dict[str, Any]]:
        """Returns extracted raw adverts.

        Args:
            response (HtmlResponse): HTML page response.

        Raises:
            ValueError: If advert data not found.

        """
        raw_data = response.xpath(".//script[@id='olx-init-config']/text()").re_first(
            r'window.__PRERENDERED_STATE__\s*=\s*"(.*)";'
        )
        if not raw_data:
            raise ValueError("Advert data not found")

        raw_data = raw_data.replace('\\"', '"').replace(r'\\"', r"\"")
        return ((json.loads(raw_data).get("listing") or {}).get("listing") or {}).get("ads") or []

    def parse(self, response: Response, **kwargs: Any) -> Any:
        """Just a stub."""
