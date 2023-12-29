from typing import Sequence

from sqlalchemy import Delete, Insert, Row, Select, Update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql.dml import ReturningInsert

from interfaces import SingletonBase
from settings import db_credentials


class DatabaseProvider(SingletonBase):
    """Provider for interacting with database."""

    _engine: AsyncEngine
    _session_maker: async_sessionmaker[AsyncSession]

    def __init__(self) -> None:
        self._engine = create_async_engine(db_credentials().build_url(use_sync_driver=False))
        self._session_maker = async_sessionmaker(bind=self._engine)

    async def select_one(self, query: Select) -> Row | None:
        """Returns one selected record from database by the given `query`."""
        async with self._session_maker() as session:
            cursor = await session.execute(query)
            return cursor.fetchone()

    async def select_all(self, query: Select) -> Sequence[Row]:
        """Returns all selected records from database by the given `query`."""
        async with self._session_maker() as session:
            cursor = await session.execute(query)
            return cursor.fetchall()

    async def insert(self, query: Insert) -> bool:
        """Executes given `query` to insert new record to database.

        Returns:
            bool: True if insertion is successful, otherwise False.

        """
        async with self._session_maker() as session:
            try:
                await session.execute(query)
                await session.commit()
            except IntegrityError:
                return False
        return True

    async def insert_with_returning(self, query: ReturningInsert) -> Row | None:
        """Executes given `query` to insert new record to database.

        Returns:
            Row: Returned result after executing query.
            None: If error occurred while inserting.

        """
        async with self._session_maker() as session:
            try:
                cursor = await session.execute(query)
                await session.commit()
                return cursor.fetchone()
            except IntegrityError:
                return None

    async def execute(self, query: Update | Delete) -> None:
        """Executes given `query` in the database."""
        async with self._session_maker() as session:
            await session.execute(query)
            await session.commit()
