from datetime import datetime
from typing import ClassVar

from aiogram.utils.markdown import hlink
from pydantic import Field

from database.schemas.base import (
    DatabaseCreateSchema,
    DatabaseReadSchema,
    DatabaseUpdateSchema,
    StrHttpUrl,
)


class AdvertRead(DatabaseReadSchema):
    """Advert schema for reading."""

    id: int
    monitoring_id: int
    monitoring_run_id: int
    url: str
    title: str
    description: str | None
    image: str | None
    price: float | None
    max_price: float | None
    currency: str | None
    sent_to_user: bool
    created_at: datetime
    updated_at: datetime

    def get_telegram_message(self) -> str:
        """Returns telegram message for advert."""
        paragraphs = [hlink(self.title, self.url)]

        if self.description:
            paragraphs.append("")
            paragraphs.append(self.description)

        if self.price is not None and self.max_price is not None:
            price_paragraph = (
                f"{int(self.price) if self.price.is_integer() else self.price} - "
                f"{int(self.max_price) if self.max_price.is_integer() else self.max_price}"
            )
        elif self.price is not None:
            price_paragraph = str(int(self.price)) if self.price.is_integer() else str(self.price)
        elif self.max_price is not None:
            price_paragraph = str(int(self.max_price)) if self.max_price.is_integer() else str(self.max_price)
        else:
            price_paragraph = None

        if price_paragraph:
            paragraphs.append("")
            if self.currency:
                price_paragraph += f" {self.currency}"
            paragraphs.append(price_paragraph)

        return "\n".join(paragraphs)


class AdvertCreate(DatabaseCreateSchema):
    """Advert schema for creation."""

    monitoring_id: int
    monitoring_run_id: int
    url: StrHttpUrl = Field(max_length=2000)
    title: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=300)
    image: str | None = Field(default=None, max_length=2000)
    price: float | None = None
    max_price: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)

    unique_fields: ClassVar[list[str]] = ["monitoring_id", "url"]
    update_fields: ClassVar[list[str]] = [
        "monitoring_run_id",
        "title",
        "description",
        "image",
        "price",
        "max_price",
        "currency",
    ]


class AdvertUpdate(DatabaseUpdateSchema):
    """Advert schema for updating."""

    monitoring_run_id: int | None = None
    title: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    image: str | None = Field(default=None, max_length=2000)
    price: float | None = None
    max_price: float | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    sent_to_user: bool | None = None
