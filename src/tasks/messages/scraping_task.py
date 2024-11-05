from pydantic import BaseModel


class ScrapingTask(BaseModel):
    """Scraping task message."""

    monitoring_id: int
    monitoring_url: str
    monitoring_run_id: int
