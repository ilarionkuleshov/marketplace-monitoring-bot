from sqlalchemy import Column, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import BIGINT, BOOLEAN, SMALLINT, TIMESTAMP, VARCHAR

from database.models.base import Base, PrimaryKeyMixin, TimestampAtMixin


class SearchQuery(Base, PrimaryKeyMixin, TimestampAtMixin):
    """Marketplace search query model."""

    __tablename__ = "search_queries"

    user_id = Column("user_id", BIGINT(), ForeignKey("users.id"), nullable=False)
    name = Column("name", VARCHAR(100), nullable=False)
    url = Column("url", VARCHAR(766), nullable=False)
    marketplace = Column("marketplace", VARCHAR(20), nullable=False)
    last_crawl_time = Column("last_crawl_time", TIMESTAMP(), nullable=True)
    crawl_interval = Column("crawl_interval", SMALLINT(), nullable=False)
    is_active: Column = Column("is_active", BOOLEAN(), nullable=False, server_default=text("TRUE"))

    __table_args__ = (UniqueConstraint(user_id, url, name="ix_search_queries_user_id_url"),)
