from contextlib import asynccontextmanager

from app.api.dependencies.db import DbProvider
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


async def init_inj_well_database(
    provider: DbProvider, settings: Settings
) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        settings.inj_well_database_path
    ) as holder:
        await init_db.init_inj_well_database(
            holder.inj_well_database_initializer
        )


async def init_neighborhood(provider: DbProvider, settings: Settings) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        settings.neighborhood_path
    ) as holder:
        await init_db.init_neighborhood(holder.neighborhood_initializer)


async def init_new_strategy_inj(
    provider: DbProvider, settings: Settings
) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        settings.new_strategy_inj_path
    ) as holder:
        await init_db.init_new_strategy_inj(
            holder.new_strategy_inj_initializer
        )


async def init_new_strategy_oil(
    provider: DbProvider, settings: Settings
) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        settings.new_strategy_oil_path
    ) as holder:
        await init_db.init_new_strategy_oil(
            holder.new_strategy_oil_initializer
        )
