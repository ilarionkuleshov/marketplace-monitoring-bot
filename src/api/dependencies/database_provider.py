from typing import Literal, Sequence, overload

from sqlalchemy import Delete, Insert, Row, Select, Update
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

    @overload
    async def select(self, query: Select, fetch_all: Literal[True]) -> Sequence[Row]:
        ...

    @overload
    async def select(self, query: Select, fetch_all: Literal[False]) -> Row | None:
        ...

    async def select(self, query: Select, fetch_all: bool) -> Sequence[Row] | Row | None:
        """Returns selected records from database.

        Args:
            query (Select): Select query to execute.
            fetch_all (bool): Whether to fetch all matching records or just one.

        """
        async with self._session_maker() as session:
            cursor = await session.execute(query)
            return cursor.fetchall() if fetch_all else cursor.fetchone()

    async def insert(self, query: Insert) -> int | None:
        """Executes given `query` to insert new record to database.

        Returns:
            int: Id of the inserted record.
            None: If insertion was unsuccessful.

        """
        async with self._session_maker() as session:
            try:
                cursor = await session.execute(query)
                await session.commit()
                return cursor.inserted_primary_key[0] if cursor.inserted_primary_key else None
            except IntegrityError:
                return None

    async def execute(self, query: Update | Delete) -> bool:
        """Executes given `query` in the database.

        Returns:
            bool: True if ok, otherwise False.

        """
        async with self._session_maker() as session:
            try:
                await session.execute(query)
                await session.commit()
                return True
            except IntegrityError:
                return False
