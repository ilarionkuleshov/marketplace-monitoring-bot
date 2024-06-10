# mypy: disable-error-code="valid-type, name-defined"

from typing import Any, Self

from sqlalchemy import update
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.future import select
from sqlalchemy.sql import ColumnExpressionArgument

from database.schemas import BaseSchema
from settings import PostgresCredentials


class DatabaseProvider:
    """Provider for the database.

    Attributes:
        engine (AsyncEngine): Database engine.
        session_maker (async_sessionmaker[AsyncSession]): Database session maker.

    """

    engine: AsyncEngine
    session_maker: async_sessionmaker[AsyncSession]

    _instance: Self | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseProvider, cls).__new__(cls)
            cls._instance._init_database()
        return cls._instance

    def _init_database(self) -> None:
        """Initializes database."""
        self.engine = create_async_engine(url=PostgresCredentials().get_url())
        self.session_maker = async_sessionmaker(bind=self.engine)

    async def get[
        T: BaseSchema
    ](self, entity: Any, *, conditions: list[ColumnExpressionArgument], schema: type[T]) -> T | None:
        """Returns one record from the database or None.

        Args:
            entity (Any): Entity to get.
            conditions (list[ColumnExpressionArgument]): Conditions for the record extraction.
            schema (type[T]): Schema for the extracted record.

        """
        async with self.session_maker() as session:
            statement = select(entity).where(*conditions)
            result = await session.execute(statement)
            if row := result.fetchone():
                return schema.model_validate(row[0])
            return None

    async def get_all[T: BaseSchema](self, entity: Any, *, schema: type[T]) -> list[T]:
        """Returns records from the database.

        Args:
            entity (Any): Entity to get.
            schema (type[T]): Schema for the extracted records.

        """
        async with self.session_maker() as session:
            statement = select(entity)
            result = await session.execute(statement)
            return [schema.model_validate(row[0]) for row in result.fetchall()]

    async def create[T: BaseSchema](self, entity: Any, *, schema: type[T]) -> T:
        """Returns created record in the database.

        Args:
            entity (Any): Entity to create.
            schema (type[T]): Schema for the created record.

        """
        async with self.session_maker() as session:
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return schema.model_validate(entity)

    async def update[
        T: BaseSchema
    ](self, entity: Any, *, data: dict[str, Any], conditions: list[ColumnExpressionArgument], schema: type[T]) -> (
        T | None
    ):
        """Returns updated record from the database or None.

        Args:
            entity (Any): Entity to update.
            data (dict[str, Any]): Data to update.
            conditions (list[ColumnExpressionArgument]): Conditions for the record updating.
            schema (type[T]): Schema for the updated record.

        """
        async with self.session_maker() as session:
            statement = update(entity).values(data).where(*conditions)
            await session.execute(statement)
            await session.commit()
            return await self.get(entity, conditions=conditions, schema=schema)
