"""Schemas for search query entity."""

from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, root_validator

from api.schemas.base import SchemaWithExample
from api.utils import check_only_one_parameter_not_none
from utils.enums import MarketplaceSpiders


class SearchQuery(BaseModel):
    """Search query schema."""

    id: int
    user_id: int
    name: str
    url: str
    marketplace: MarketplaceSpiders
    last_crawl_time: datetime | None
    crawl_interval: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchQueryCreate(SchemaWithExample):
    """Schema to create search query."""

    user_id: int | None = None
    user_telegram_id: int | None = None
    name: str = Field(..., max_length=100)
    url: HttpUrl
    marketplace: str
    crawl_interval: int = Field(..., ge=15)
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

    # pylint: disable=E0213
    @root_validator(pre=True)
    def validate_user_ids(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Returns field `values` after validation user ids."""
        check_only_one_parameter_not_none(user_id=values["user_id"], user_telegram_id=values["user_telegram_id"])
        return values

    @classmethod
    def example(cls) -> Self:
        """See `SchemaWithExample` class."""
        return cls(
            user_telegram_id=123456,
            name="example_name",
            url=HttpUrl("https://example.com"),
            marketplace=MarketplaceSpiders.SHAFA,
            crawl_interval=15,
            is_active=True,
        )


class SearchQueryUpdate(SchemaWithExample):
    """Schema to create search query."""

    name: str | None = Field(None, max_length=100)
    crawl_interval: int | None = Field(None, ge=15)
    is_active: bool | None = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def example(cls) -> Self:
        """See `SchemaWithExample` class."""
        return cls(
            name="example_name",
            crawl_interval=25,
            is_active=False,
        )
