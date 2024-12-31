import json
from typing import Any, AsyncIterator

from fastcrawl import Request, Response
from parsel import Selector

from database.schemas import AdvertCreate
from scrapers.crawlers.base_advert_crawler import BaseAdvertCrawler


class OlxUaCrawler(BaseAdvertCrawler):
    """Crawler for scraping adverts from `olx.ua`."""

    async def generate_requests(self) -> AsyncIterator[Request]:
        """Yields a request to start scraping."""
        yield Request(url=self.monitoring_url, callback=self.parse_search_page)

    async def parse_search_page(self, response: Response) -> AsyncIterator[AdvertCreate | Request]:
        """Parses search page.

        Args:
            response (Response): Page response.

        Yields:
            AdvertCreate: Parsed advert.
            Request: Next page request.

        """
        raw_adverts = self._get_raw_adverts(response.selector)

        for raw_advert in raw_adverts:
            if "url" not in raw_advert or "title" not in raw_advert:
                self.logger.warning("Skipping advert, missing required data: %s", raw_advert)
                continue

            price_data = (raw_advert.get("price") or {}).get("regularPrice") or {}
            yield AdvertCreate(
                monitoring_id=self.monitoring_id,
                monitoring_run_id=self.monitoring_run_id,
                url=raw_advert["url"],
                title=self.crop_str(raw_advert["title"], 100),
                description=self.crop_str(raw_advert["description"], 300) if raw_advert.get("description") else None,
                image=raw_advert["photos"][0] if raw_advert.get("photos") else None,
                price=price_data.get("value") or None,
                currency=price_data.get("currencyCode") or None,
            )

        if next_page_url := response.selector.xpath(".//a[@data-cy='pagination-forward']/@href").get():
            yield Request(url=response.url.join(next_page_url), callback=self.parse_search_page)

    def _get_raw_adverts(self, selector: Selector) -> list[dict[str, Any]]:
        """Returns extracted raw adverts.

        Args:
            selector (Selector): Page selector.

        Raises:
            ValueError: If advert data not found.

        """
        raw_data = selector.xpath(".//script[@id='olx-init-config']/text()").re_first(
            r'window.__PRERENDERED_STATE__\s*=\s*"(.*)";'
        )
        if not raw_data:
            raise ValueError("Advert data not found")

        raw_data = raw_data.replace("\\\\", "\\").replace(r"\"", '"')
        raw_data = json.dumps(json.loads(raw_data), ensure_ascii=False)
        raw_data = raw_data.replace("<br />", "")
        return ((json.loads(raw_data).get("listing") or {}).get("listing") or {}).get("ads") or []
