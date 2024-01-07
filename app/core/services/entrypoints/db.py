from contextlib import asynccontextmanager

from app.api.dependencies.dao.provider import DbProvider
from app.core.config.settings import Settings
from app.core.services import init_db


async def init_field_replace(provider: DbProvider, settings: Settings) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        settings.field_replace_path
    ) as holder:
        await init_db.init_field_replace(holder.field_replace_initializer)


async def init_reservoir_replace(
    provider: DbProvider, settings: Settings
) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        settings.reservoir_replace_path
    ) as holder:
        await init_db.init_reservoir_replace(
            holder.reservoir_replace_initializer
        )


async def init_layer_replace(provider: DbProvider, settings: Settings) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        settings.layer_replace_path
    ) as holder:
        await init_db.init_layer_replace(holder.layer_replace_initializer)


async def init_monthly_report(
    provider: DbProvider, settings: Settings
) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        settings.monthly_report_path
    ) as holder:
        await init_db.init_monthly_report(holder.monthly_report_initializer)


async def init_well_profile(provider: DbProvider, settings: Settings) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        settings.well_profile_path
    ) as holder:
        await init_db.init_well_profile(holder.well_profile_initializer)
