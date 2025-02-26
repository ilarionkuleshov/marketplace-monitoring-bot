from fastcrawl import BasePipeline
from faststream.rabbit import RabbitBroker

from database.schemas import AdvertCreate
from settings import TasksSettings
from tasks.queues import SCRAPING_RESULTS_QUEUE


class PublishAdvertPipeline(BasePipeline):
    """Pipeline to publish advert to message broker."""

    allowed_items = [AdvertCreate]

    _broker: RabbitBroker

    async def on_crawler_start(self) -> None:
        """Initializes message broker."""
        self._broker = RabbitBroker(TasksSettings().get_broker_url())

    async def on_crawler_finish(self) -> None:
        """Closes message broker."""
        await self._broker.close()

    async def process_item(self, item: AdvertCreate) -> AdvertCreate:
        """Publishes advert to message broker.

        Args:
            item (AdvertCreate): Advert to publish.

        Returns:
            AdvertCreate: Published advert.

        """
        async with self._broker:
            await self._broker.publish(message=item, queue=SCRAPING_RESULTS_QUEUE, persist=True)
        return item
