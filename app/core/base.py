"""Импорты класса Base и всех моделей для Alembic."""
# import asyncio

# from sqlalchemy.schema import CreateSchema

# from app.core.config import settings
from app.core.local_db import Base, engine  # noqa
from app.models.monthly_report import MonthlyReport  # noqa
from app.models.utility import ReservoirReplace  # noqa
from app.models.well_profile import WellProfile  # noqa

# def prepare_base(conn):
#     schema = settings.util_table_schema
#     if not conn.dialect.has_schema(conn, schema):
#         conn.execute(CreateSchema(schema))
#         conn.commit()


# async def async_main():
#     async with engine.connect() as conn:
#         await conn.run_sync(prepare_base)

# asyncio.run(async_main())
