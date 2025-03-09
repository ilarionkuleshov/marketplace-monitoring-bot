from .base_advert_crawler import BaseAdvertCrawler
from .olx_ua_crawler import OlxUaCrawler
from .shafa_ua_crawler import ShafaUaCrawler

MARKETPLACE_CRAWLERS_MAPPING: dict[str, type[BaseAdvertCrawler]] = {
    "Olx UA": OlxUaCrawler,
    "Shafa UA": ShafaUaCrawler,
}
