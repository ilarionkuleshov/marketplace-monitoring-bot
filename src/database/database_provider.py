from typing import Self

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
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
    ](self, *, model: type[DeclarativeMeta], conditions: list[ColumnExpressionArgument], return_schema: type[T]) -> (
        T | None
    ):
        """Returns one extracted record from the database.

        Args:
            model (type[DeclarativeMeta]): Database model to get from.
            conditions (list[ColumnExpressionArgument]): Conditions for extraction.
            return_schema (type[T]): Schema for the extracted record.

        """
        async with self._session_maker() as session:
            statement = select(model).where(*conditions)
            cursor = await session.execute(statement)
            if record := cursor.fetchone():
                return return_schema.model_validate(record[0])
            return None

    async def get_all[
        T: BaseSchema
    ](
        self,
        *,
        model: type[DeclarativeMeta],
        conditions: list[ColumnExpressionArgument] | None = None,
        return_schema: type[T],
    ) -> list[T]:
        """Returns all extracted records from the database.

        Args:
            model (type[DeclarativeMeta]): Database model to get from.
            conditions (list[ColumnExpressionArgument] | None): Conditions for extraction. Default is None.
            return_schema (type[T]): Schema for the extracted records.

        """
        if conditions is None:
            conditions = []

        async with self._session_maker() as session:
            statement = select(model).where(*conditions)
            cursor = await session.execute(statement)
            return [return_schema.model_validate(record[0]) for record in cursor.fetchall()]

    async def create[
        T: BaseSchema
    ](self, *, model: type[DeclarativeMeta], data: BaseSchema, return_schema: type[T]) -> T:
        """Creates record in the database.

        Args:
            model (type[DeclarativeMeta]): Database model for creation.
            data (BaseSchema): Data for the model.
            return_schema (type[T]): Schema for the created record.

        Returns:
            T: Created record in the database.

        """
        async with self._session_maker() as session:
            record = model(**data.model_dump(exclude_none=True))
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return return_schema.model_validate(record)

    async def update[
        T: BaseSchema
    ](
        self,
        *,
        model: type[DeclarativeMeta],
        data: BaseSchema,
        conditions: list[ColumnExpressionArgument],
        return_schema: type[T],
    ) -> T:
        """Updates record in the database.

        Args:
            model (type[DeclarativeMeta]): Database model for updating.
            data (BaseSchema): Data for the model.
            conditions (list[ColumnExpressionArgument]): Conditions for updating.
            return_schema (type[T]): Schema for the updated record.

        Returns:
            T: Updated record in the database.

        Raises:
            ValueError: Number of records to update does not equal one.

        """
        async with self._session_maker() as session:
            statement = update(model).where(*conditions).values(data.model_dump(exclude_none=True))
            cursor = await session.execute(statement)

            if cursor.rowcount != 1:
                raise ValueError(f"Number of records to update ({cursor.rowcount}) does not equal one")

            await session.commit()
            return await self.get(model=model, conditions=conditions, return_schema=return_schema)

    async def delete(self, *, model: type[DeclarativeMeta], conditions: list[ColumnExpressionArgument]) -> None:
        """Deletes records from the database.

        Args:
            model (type[DeclarativeMeta]): Database model to delete from.
            conditions (list[ColumnExpressionArgument]): Conditions for deletion.

        Raises:
            ValueError: Number of records to delete does not equal one.

        """
        async with self._session_maker() as session:
            statement = delete(model).where(*conditions)
            cursor = await session.execute(statement)

            if cursor.rowcount != 1:
                raise ValueError(f"Number of records to delete ({cursor.rowcount}) does not equal one")
            await session.commit()
