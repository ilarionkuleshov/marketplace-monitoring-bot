from faststream.rabbit import RabbitRouter

from tasks.queues import SCRAPING_TASKS_QUEUE

router = RabbitRouter()


@router.subscriber(SCRAPING_TASKS_QUEUE)
async def handle_scraping_task() -> None:
    """Handles scraping task."""
