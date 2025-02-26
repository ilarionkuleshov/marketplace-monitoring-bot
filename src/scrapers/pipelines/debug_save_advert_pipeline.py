from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from fastcrawl import BasePipeline

from database.schemas import AdvertCreate


class DebugSaveAdvertPipeline(BasePipeline):
    """Pipeline to save adverts locally for debugging purposes.

    Attributes:
        storage_path (Path): The path to save the adverts.

    """

    allowed_items = [AdvertCreate]

    storage_path: Path

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        current_datetime = datetime.now().replace(microsecond=0)
        self.storage_path = (
            Path("./storage/adverts/") / current_datetime.date().isoformat() / current_datetime.time().isoformat()
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def process_item(self, item: AdvertCreate) -> AdvertCreate:
        """Saves the advert to a file.

        Args:
            item (AdvertCreate): The advert to save.

        Returns:
            AdvertCreate: The saved advert.

        """
        advert_id = hashlib.md5(str(item.url).encode()).hexdigest()
        advert_path = self.storage_path / f"{advert_id}.json"
        advert_path.write_text(item.model_dump_json(indent=4), encoding="utf-8")
        return item
