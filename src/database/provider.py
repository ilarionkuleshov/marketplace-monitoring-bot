from contextlib import asynccontextmanager
from typing import AsyncIterator, overload

from sqlalchemy import Select, UnaryExpression, delete, select, update
from sqlalchemy.dialects.postgresql import insert
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
    ](
        self,
        *,
        model: DatabaseModelType,
        filters: list[ColumnExpressionArgument],
        order_by: list[UnaryExpression] | None = None,
        read_schema: type[T],
    ) -> (T | None):
        """Returns a single row from the database.

        Args:
            model (DatabaseModelType): The database model for the query.
            filters (list[ColumnExpressionArgument]): The conditions to filter the query.
            order_by (list[UnaryExpression] | None): The columns to order the query. Default is None.
            read_schema (type[T]): The schema to validate the result.

        """
        query = select(model).where(*filters)
        if order_by:
            query = query.order_by(*order_by)

        cursor = await self._session.execute(query)
        if row := cursor.scalars().first():
            return read_schema.model_validate(row)
        return None

    async def get_by_query[T: DatabaseReadSchema](self, *, query: Select, read_schema: type[T]) -> T | None:
        """Returns a single row from the database by query.

        Args:
            query (Select): The query to execute.
            read_schema (type[T]): The schema to validate the result.

        """
        cursor = await self._session.execute(query)
        if row := cursor.mappings().one():
            return read_schema.model_validate(row)
        return None

    async def get_all[
        T: DatabaseReadSchema
    ](
        self,
        *,
        model: DatabaseModelType,
        filters: list[ColumnExpressionArgument] | None = None,
        order_by: list[UnaryExpression] | None = None,
        read_schema: type[T],
    ) -> list[T]:
        """Returns all rows from the database.

        Args:
            model (DatabaseModelType): The database model for the query.
            filters (list[ColumnExpressionArgument] | None): The conditions to filter the query. Default is None.
            order_by (list[UnaryExpression] | None): The columns to order the query. Default is None.
            read_schema (type[T]): The schema to validate the result.

        """
        query = select(model)
        if filters:
            query = query.where(*filters)
        if order_by:
            query = query.order_by(*order_by)

        cursor = await self._session.execute(query)
        return [read_schema.model_validate(row) for row in cursor.scalars().all()]

    async def get_all_by_query[T: DatabaseReadSchema](self, *, query: Select, read_schema: type[T]) -> list[T]:
        """Returns all rows from the database by query.

        Args:
            query (Select): The query to execute.
            read_schema (type[T]): The schema to validate the result.

        """
        cursor = await self._session.execute(query)
        return [read_schema.model_validate(row) for row in cursor]

    @overload
    async def create[
        T: DatabaseReadSchema
    ](
        self,
        *,
        model: DatabaseModelType,
        data: DatabaseCreateSchema,
        update_on_conflict: bool = False,
        read_schema: type[T],
    ) -> T: ...

    @overload
    async def create(
        self,
        *,
        model: DatabaseModelType,
        data: DatabaseCreateSchema,
        update_on_conflict: bool = False,
        read_schema: None = None,
    ) -> None: ...

    async def create[
        T: DatabaseReadSchema
    ](
        self,
        *,
        model: DatabaseModelType,
        data: DatabaseCreateSchema,
        update_on_conflict: bool = False,
        read_schema: type[T] | None = None,
    ) -> (T | None):
        """Creates a new row in the database.

        Args:
            model (DatabaseModelType): The database model for the query.
            data (DatabaseCreateSchema): The data to insert.
            update_on_conflict (bool): Whether to update on conflict. Default is False.
            read_schema (type[T] | None): The schema to validate the result.
                If not provided, None will be returned. Default is None.

        Returns:
            T: Created row.
            None: If read_schema not provided.

        """
        query = insert(model).values(**data.model_dump_for_insert())
        if update_on_conflict:
            query = query.on_conflict_do_update(
                index_elements=data.unique_fields,
                set_={el.name: el for el in query.excluded if el.name in data.update_fields},
            )
        cursor = await self._session.execute(query)

        if read_schema is None:
            return None
        row = await self._session.get(model, cursor.inserted_primary_key)
        return read_schema.model_validate(row)

    @overload
    async def update[
        T: DatabaseReadSchema
    ](
        self,
        *,
        model: DatabaseModelType,
        data: DatabaseUpdateSchema,
        filters: list[ColumnExpressionArgument],
        read_schema: type[T],
    ) -> T: ...

    @overload
    async def update(
        self,
        *,
        model: DatabaseModelType,
        data: DatabaseUpdateSchema,
        filters: list[ColumnExpressionArgument],
        read_schema: None = None,
    ) -> None: ...

    async def update[
        T: DatabaseReadSchema
    ](
        self,
        *,
        model: DatabaseModelType,
        data: DatabaseUpdateSchema,
        filters: list[ColumnExpressionArgument],
        read_schema: type[T] | None = None,
    ) -> (T | None):
        """Updates a row in the database.

        Args:
            model (DatabaseModelType): The database model for the query.
            data (DatabaseUpdateSchema): The data to update.
            filters (list[ColumnExpressionArgument]): The conditions to filter the query.
            read_schema (type[T] | None): The schema to validate the result.
                If not provided, None will be returned. Default is None.

        Returns:
            T: Updated row.
            None: If read_schema not provided.

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

        if read_schema is None:
            return None
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
        await self._session.execute(query)
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
