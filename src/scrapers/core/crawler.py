import logging
from abc import ABC


class Crawler(ABC):
    """Base for all crawlers.

    Attributes:
        logger (logging.Logger): Logger for the crawler.

    """

    logger: logging.Logger

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
