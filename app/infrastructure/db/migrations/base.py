"""Импорты класса Base и всех моделей для Alembic."""
import asyncio

from sqlalchemy import Connection
from sqlalchemy.schema import CreateSchema

from app.core.config.settings import settings
from app.infrastructure.db.factories.local import create_engine
from app.infrastructure.db.models.local import Base  # noqa


def prepare_base(conn: Connection) -> None:
    schema = settings.util_table_schema
    if not conn.dialect.has_schema(conn, schema):
        conn.execute(CreateSchema(schema))
        conn.commit()


async def async_main() -> None:
    try:
        engine = create_engine(settings)
        async with engine.connect() as conn:
            await conn.run_sync(prepare_base)
    finally:
        await engine.dispose()


asyncio.run(async_main())
