from pydantic import BaseModel, ConfigDict


class ScrapingTask(BaseModel):
    """Scraping task message."""

    monitoring_id: int
    monitoring_url: str
    monitoring_run_id: int

    model_config = ConfigDict(from_attributes=True)
