from settings import ScrapersSettings

scrapers_settings = ScrapersSettings()

LOG_LEVEL = scrapers_settings.log_level
USER_AGENT = scrapers_settings.user_agent
CONCURRENT_REQUESTS = scrapers_settings.concurrent_requests

BOT_NAME = "scrapers"
SPIDER_MODULES = ["scrapers.spiders"]
NEWSPIDER_MODULE = "scrapers.spiders"
ROBOTSTXT_OBEY = False
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
