from sqlalchemy import Insert, Row, Select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from interfaces import SingletonBase
from settings import db_credentials


class DatabaseProvider(SingletonBase):
    """Provider for interacting with database."""

    _engine: AsyncEngine
    _session_maker: async_sessionmaker[AsyncSession]

    def __init__(self) -> None:
        self._engine = create_async_engine(db_credentials().build_url(use_sync_driver=False))
        self._session_maker = async_sessionmaker(bind=self._engine)

    async def insert(self, query: Insert) -> bool:
        """Executes given `query` to insert new record to database.

        Returns:
            bool: True if insertion is successful, otherwise False.

        """
        async with self._session_maker() as session:
            try:
                await session.execute(query)
            except IntegrityError:
                return False
            await session.commit()
        return True

    async def select_one(self, query: Select) -> Row | None:
        """Returns selected record from database by the given `query`."""
        async with self._session_maker() as session:
            cursor = await session.execute(query)
            return cursor.fetchone()
