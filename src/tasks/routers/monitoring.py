from typing import AsyncIterator

from faststream.rabbit import RabbitRouter

from tasks.messages import ScrapingTask
from tasks.queues import MONITORING_CHECK_TASKS_QUEUE, SCRAPING_TASKS_QUEUE

router = RabbitRouter()


@router.subscriber(MONITORING_CHECK_TASKS_QUEUE)
@router.publisher(SCRAPING_TASKS_QUEUE)
async def handle_monitoring_check_task() -> AsyncIterator[ScrapingTask]:
    """Handles monitoring check task."""
    raise NotImplementedError
