from faststream.rabbit import RabbitQueue

MONITORING_CHECK_TASKS_QUEUE = RabbitQueue("monitoring_check_tasks", durable=True)
SCRAPING_TASKS_QUEUE = RabbitQueue("scraping_tasks", durable=True)
