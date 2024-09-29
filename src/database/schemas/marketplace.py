from database.schemas.base import DatabaseSchema


class MarketplaceRead(DatabaseSchema):
    """Marketplace schema for reading."""

    id: int
    name: str
    url: str
