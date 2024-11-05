from faststream.rabbit import RabbitRouter

from tasks.queues import MONITORING_CHECK_TASKS_QUEUE

router = RabbitRouter()


@router.subscriber(MONITORING_CHECK_TASKS_QUEUE)
async def handle_monitoring_check_task():
    """Handles monitoring check task."""
    raise NotImplementedError
