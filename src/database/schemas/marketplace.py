from database.schemas.base import BaseSchema


class MarketplaceRead(BaseSchema):
    """Marketplace read schema."""

    id: int
    name: str
    url: str
