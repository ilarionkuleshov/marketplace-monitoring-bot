from typing import Self

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.sql import ColumnExpressionArgument

from database.schemas import BaseSchema
from settings import PostgresCredentials


# mypy: disable-error-code="valid-type, name-defined"
class DatabaseProvider:
    """Provider for the database."""

    _engine: AsyncEngine
    _session_maker: async_sessionmaker[AsyncSession]
    _instance: Self | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseProvider, cls).__new__(cls)
            cls._instance._init_database()
        return cls._instance

    def _init_database(self) -> None:
        """Initializes database."""
        self._engine = create_async_engine(url=PostgresCredentials().get_url(use_sync_driver=False))
        self._session_maker = async_sessionmaker(bind=self._engine)

    async def get[
        T: BaseSchema
    ](self, model: type[DeclarativeMeta], *, conditions: list[ColumnExpressionArgument], schema: type[T]) -> T | None:
        """Returns one extracted record from the database.

        Args:
            model (type[DeclarativeMeta]): Database model to get from.
            conditions (list[ColumnExpressionArgument]): Conditions for extraction.
            schema (type[T]): Schema for the extracted record.

        """
        async with self._session_maker() as session:
            statement = select(model).where(*conditions)
            result = await session.execute(statement)
            if row := result.fetchone():
                return schema.model_validate(row[0])
            return None

    async def get_all[
        T: BaseSchema
    ](self, model: type[DeclarativeMeta], *, conditions: list[ColumnExpressionArgument], schema: type[T]) -> list[T]:
        """Returns all extracted records from the database.

        Args:
            model (type[DeclarativeMeta]): Database model to get from.
            conditions (list[ColumnExpressionArgument]): Conditions for extraction.
            schema (type[T]): Schema for the extracted records.

        """
        async with self._session_maker() as session:
            statement = select(model).where(*conditions)
            result = await session.execute(statement)
            return [schema.model_validate(row[0]) for row in result.fetchall()]

    async def create[T: BaseSchema](self, record: DeclarativeMeta, *, schema: type[T]) -> T:
        """Creates record in the database.

        Args:
            record (DeclarativeMeta): Record to create.
            schema (type[T]): Schema for the created record.

        Returns:
            T: Created record in the database.

        """
        async with self._session_maker() as session:
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return schema.model_validate(record)

    async def delete(self, model: type[DeclarativeMeta], *, conditions: list[ColumnExpressionArgument]) -> None:
        """Deletes records from the database.

        Args:
            model (type[DeclarativeMeta]): Database model to delete from.
            conditions (list[ColumnExpressionArgument]): Conditions for deletion.

        """
        async with self._session_maker() as session:
            statement = delete(model).where(*conditions)
            await session.execute(statement)
            await session.commit()
