from database.schemas.base import DatabaseReadSchema


class MarketplaceRead(DatabaseReadSchema):
    """Marketplace schema for reading."""

    id: int
    name: str
    url: str
