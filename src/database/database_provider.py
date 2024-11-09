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
    """Provider for the database."""

    _engine: AsyncEngine
    _session_maker: async_sessionmaker[AsyncSession]

    def __init__(self) -> None:
        self._engine = create_async_engine(url=DatabaseSettings().get_url())
        self._session_maker = async_sessionmaker(bind=self._engine)

    async def get[
        T: DatabaseReadSchema
    ](self, *, model: DatabaseModelType, read_schema: type[T], filters: list[ColumnExpressionArgument]) -> T | None:
        """Returns a single row from the database.

        Args:
            model (DatabaseModelType): The database model for the query.
            read_schema (type[T]): The schema to validate the result.
            filters (list[ColumnExpressionArgument]): The conditions to filter the query.

        """
        async with self._session_maker() as session:
            query = select(model).where(*filters)
            cursor = await session.execute(query)
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
        async with self._session_maker() as session:
            query = select(model)
            if filters:
                query = query.where(*filters)
            cursor = await session.execute(query)
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
        async with self._session_maker() as session:
            row = model(**data.model_dump_for_insert())
            session.add(row)
            await session.commit()
            await session.refresh(row)
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
        async with self._session_maker() as session:
            select_query = select(model).where(*filters)
            select_cursor = await session.execute(select_query)

            rows = select_cursor.scalars().all()
            if len(rows) != 1:
                raise ValueError(f"Number of rows to update ({len(rows)}) does not equal one")
            row = rows[0]

            update_query = update(model).where(*filters).values(data.model_dump_for_update())
            await session.execute(update_query)
            await session.commit()

            await session.refresh(row)
            return read_schema.model_validate(row)

    async def delete(self, *, model: DatabaseModelType, filters: list[ColumnExpressionArgument]) -> None:
        """Deletes rows from the database.

        Args:
            model (DatabaseModelType): The database model for the query.
            filters (list[ColumnExpressionArgument]): The conditions to filter the query.

        Raises:
            ValueError: If no rows to delete.

        """
        async with self._session_maker() as session:
            query = delete(model).where(*filters)
            cursor = await session.execute(query)
            if cursor.rowcount == 0:
                raise ValueError("No rows to delete")
            await session.commit()
