from contextlib import asynccontextmanager

from app.api.dependencies.db import DbProvider
from app.core.services import init_db
from app.infrastructure.files.config.models.paths import Paths


async def init_field_replace(provider: DbProvider, paths: Paths) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        paths.field_replace
    ) as holder:
        await init_db.init_field_replace(holder.field_replace_initializer)


async def init_reservoir_replace(provider: DbProvider, paths: Paths) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        paths.reservoir_replace
    ) as holder:
        await init_db.init_reservoir_replace(
            holder.reservoir_replace_initializer
        )


async def init_layer_replace(provider: DbProvider, paths: Paths) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        paths.layer_replace
    ) as holder:
        await init_db.init_layer_replace(holder.layer_replace_initializer)


async def init_monthly_report(provider: DbProvider, paths: Paths) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        paths.monthly_report
    ) as holder:
        await init_db.init_monthly_report(holder.monthly_report_initializer)


async def init_well_profile(provider: DbProvider, paths: Paths) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        paths.well_profile
    ) as holder:
        await init_db.init_well_profile(holder.well_profile_initializer)


async def init_inj_well_database(provider: DbProvider, paths: Paths) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        paths.inj_well_database
    ) as holder:
        await init_db.init_inj_well_database(
            holder.inj_well_database_initializer
        )


async def init_neighborhood(provider: DbProvider, paths: Paths) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        paths.neighborhood
    ) as holder:
        await init_db.init_neighborhood(holder.neighborhood_initializer)


async def init_new_strategy_inj(provider: DbProvider, paths: Paths) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        paths.new_strategy_inj
    ) as holder:
        await init_db.init_new_strategy_inj(
            holder.new_strategy_inj_initializer
        )


async def init_new_strategy_oil(provider: DbProvider, paths: Paths) -> None:
    async with asynccontextmanager(provider.file_local_dao)(
        paths.new_strategy_oil
    ) as holder:
        await init_db.init_new_strategy_oil(
            holder.new_strategy_oil_initializer
        )
