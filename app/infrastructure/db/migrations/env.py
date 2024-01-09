import asyncio
import os
import re
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.infrastructure.db.models.local import Base

load_dotenv()

config = context.config

url_tokens = {
    "POSTGRES_DB": os.getenv("POSTGRES_DB", ""),
    "POSTGRES_USER": os.getenv("POSTGRES_USER", ""),
    "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
    "DB_HOST": os.getenv("DB_HOST", ""),
    "DB_PORT": os.getenv("DB_PORT", ""),
}
url = config.get_main_option("sqlalchemy.url")
url = re.sub(r"\${(.+?)}", lambda m: url_tokens[m.group(1)], url)
config.set_main_option("sqlalchemy.url", url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        user_module_prefix="app.infrastructure.db.migrations.types.",
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        user_module_prefix="app.infrastructure.db.migrations.types.",
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
