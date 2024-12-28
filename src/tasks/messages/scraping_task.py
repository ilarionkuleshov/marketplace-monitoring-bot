from database.schemas import DatabaseReadSchema


class ScrapingTask(DatabaseReadSchema):
    """Scraping task message."""

    monitoring_id: int
    monitoring_url: str
    monitoring_run_id: int
