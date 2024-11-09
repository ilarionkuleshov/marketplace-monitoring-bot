from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.database_provider import DatabaseProvider
from settings import DatabaseSettings

engine: AsyncEngine = create_async_engine(url=DatabaseSettings().get_url())
session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)


async def get_database_provider() -> AsyncIterator[DatabaseProvider]:
    """Yields database provider for dependency injection."""
    session = session_maker()
    try:
        yield DatabaseProvider(session)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
