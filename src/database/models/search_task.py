from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import BIGINT, JSON, VARCHAR

from database.models.base import Base, PrimaryKeyMixin, StatusMixin, TimestampAtMixin


class SearchTask(Base, PrimaryKeyMixin, StatusMixin, TimestampAtMixin):
    """Search task model."""

    __tablename__ = "search_tasks"

    search_query_id = Column("search_query_id", BIGINT(), ForeignKey("search_queries.id"), nullable=False)
    log_file = Column("log_file", VARCHAR(100), nullable=True)
    statistics = Column("statistics", JSON(), nullable=True)
