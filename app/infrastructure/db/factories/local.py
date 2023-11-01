from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config.settings import Settings


def create_pool(settings: Settings) -> async_sessionmaker[AsyncSession]:
    engine = create_engine(settings)
    return create_session_maker(engine)


def create_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(str(settings.local_database_url))


def create_session_maker(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine)
