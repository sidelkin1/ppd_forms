from contextlib import asynccontextmanager

from app.api.dependencies.dao.provider import DbProvider
from app.core.services import init_db


async def init_field_replace(provider: DbProvider) -> None:
    async with asynccontextmanager(provider.local_dao)() as holder:
        await init_db.init_field_replace(holder.field_replace_initializer)


async def init_reservoir_replace(provider: DbProvider) -> None:
    async with asynccontextmanager(provider.local_dao)() as holder:
        await init_db.init_reservoir_replace(
            holder.reservoir_replace_initializer
        )


async def init_layer_replace(provider: DbProvider) -> None:
    async with asynccontextmanager(provider.local_dao)() as holder:
        await init_db.init_layer_replace(holder.layer_replace_initializer)


async def init_monthly_report(provider: DbProvider) -> None:
    async with asynccontextmanager(provider.local_dao)() as holder:
        await init_db.init_monthly_report(holder.monthly_report_initializer)


async def init_well_profile(provider: DbProvider) -> None:
    async with asynccontextmanager(provider.local_dao)() as holder:
        await init_db.init_well_profile(holder.well_profile_initializer)
