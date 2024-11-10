from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql import ColumnExpressionArgument

from database.models import DatabaseModelType
from database.schemas import (
    DatabaseCreateSchema,
    DatabaseReadSchema,
    DatabaseUpdateSchema,
)
from settings import DatabaseSettings


# mypy: disable-error-code="valid-type, name-defined"
class DatabaseProvider:
    """Provider for the database.

    Args:
        session (AsyncSession): The session to use for the database.

    """

    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get[
        T: DatabaseReadSchema
    ](self, *, model: DatabaseModelType, read_schema: type[T], filters: list[ColumnExpressionArgument]) -> T | None:
        """Returns a single row from the database.

        Args:
            model (DatabaseModelType): The database model for the query.
            read_schema (type[T]): The schema to validate the result.
            filters (list[ColumnExpressionArgument]): The conditions to filter the query.

        """
        query = select(model).where(*filters)
        cursor = await self._session.execute(query)
        if row := cursor.scalars().first():
            return read_schema.model_validate(row)
        return None

    async def get_all[
        T: DatabaseReadSchema
    ](
        self, *, model: DatabaseModelType, read_schema: type[T], filters: list[ColumnExpressionArgument] | None = None
    ) -> list[T]:
        """Returns all rows from the database.

        Args:
            model (DatabaseModelType): The database model for the query.
            read_schema (type[T]): The schema to validate the result.
            filters (list[ColumnExpressionArgument] | None): The conditions to filter the query. Default is None.

        """
        query = select(model)
        if filters:
            query = query.where(*filters)
        cursor = await self._session.execute(query)
        return [read_schema.model_validate(row) for row in cursor.scalars().all()]

    async def create[
        T: DatabaseReadSchema
    ](self, *, model: DatabaseModelType, data: DatabaseCreateSchema, read_schema: type[T]) -> T:
        """Creates a new row in the database.

        Args:
            model (DatabaseModelType): The database model for the query.
            data (DatabaseCreateSchema): The data to insert.
            read_schema (type[T]): The schema to validate the result.

        """
        row = model(**data.model_dump_for_insert())
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return read_schema.model_validate(row)

    async def update[
        T: DatabaseReadSchema
    ](
        self,
        *,
        model: DatabaseModelType,
        data: DatabaseUpdateSchema,
        read_schema: type[T],
        filters: list[ColumnExpressionArgument],
    ) -> T:
        """Updates a row in the database.

        Args:
            model (DatabaseModelType): The database model for the query.
            data (DatabaseUpdateSchema): The data to update.
            read_schema (type[T]): The schema to validate the result.
            filters (list[ColumnExpressionArgument]): The conditions to filter the query.

        """
        select_query = select(model).where(*filters)
        select_cursor = await self._session.execute(select_query)

        rows = select_cursor.scalars().all()
        if len(rows) != 1:
            raise ValueError(f"Number of rows to update ({len(rows)}) does not equal one")
        row = rows[0]

        update_query = update(model).where(*filters).values(data.model_dump_for_update())
        await self._session.execute(update_query)
        await self._session.flush()

        await self._session.refresh(row)
        return read_schema.model_validate(row)

    async def delete(self, *, model: DatabaseModelType, filters: list[ColumnExpressionArgument]) -> None:
        """Deletes rows from the database.

        Args:
            model (DatabaseModelType): The database model for the query.
            filters (list[ColumnExpressionArgument]): The conditions to filter the query.

        Raises:
            ValueError: If no rows to delete.

        """
        query = delete(model).where(*filters)
        cursor = await self._session.execute(query)
        if cursor.rowcount == 0:
            raise ValueError("No rows to delete")
        await self._session.flush()


engine: AsyncEngine = create_async_engine(url=DatabaseSettings().get_url())
session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)


@asynccontextmanager
async def get_database() -> AsyncIterator[DatabaseProvider]:
    """Yields database provider."""
    session = session_maker()
    try:
        yield DatabaseProvider(session)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_database_dep() -> AsyncIterator[DatabaseProvider]:
    """Yields database provider for dependency injection."""
    async with get_database() as database:
        yield database
