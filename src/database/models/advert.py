from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import BIGINT, FLOAT, VARCHAR

from database.models.base import Base, PrimaryKeyMixin, StatusMixin, TimestampAtMixin


class Advert(Base, PrimaryKeyMixin, StatusMixin, TimestampAtMixin):
    """Marketplace advert model."""

    __tablename__ = "adverts"

    search_query_id = Column("search_query_id", BIGINT(), ForeignKey("search_queries.id"), nullable=False)
    external_id = Column("external_id", VARCHAR(100), nullable=False)
    url = Column("url", VARCHAR(1000), nullable=False)
    image = Column("image", VARCHAR(1000), nullable=True)
    title = Column("title", VARCHAR(1000), nullable=False)
    description = Column("description", VARCHAR(200), nullable=True)
    value: Column = Column("value", FLOAT(), nullable=True)
    max_value: Column = Column("max_value", FLOAT(), nullable=True)
    currency = Column("currency", VARCHAR(3), nullable=True)

    __table_args__ = (UniqueConstraint(search_query_id, external_id, name="ix_adverts_search_query_id_external_id"),)
