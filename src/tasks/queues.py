from faststream.rabbit import RabbitQueue

TRIGGER_SCRAPING_TASKS_QUEUE = RabbitQueue("trigger_scraping_tasks", durable=True)
SCRAPING_TASKS_QUEUE = RabbitQueue("scraping_tasks", durable=True)
