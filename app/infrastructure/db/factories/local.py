from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.db.config.models.local import PostgresSettings


def create_pool(
    settings: PostgresSettings,
) -> async_sessionmaker[AsyncSession]:
    engine = create_engine(settings)
    return create_session_maker(engine)


def create_engine(settings: PostgresSettings) -> AsyncEngine:
    return create_async_engine(str(settings.url))


def create_session_maker(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine)
