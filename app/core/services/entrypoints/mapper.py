from contextlib import asynccontextmanager

from app.api.dependencies.db import DbProvider
from app.core.services import init_mapper


async def init_field_mapper(provider: DbProvider) -> None:
    async with asynccontextmanager(provider.local_dao)() as holder:
        await init_mapper.init_field_mapper(holder.local_field_replace)


async def init_reservoir_mapper(provider: DbProvider) -> None:
    async with asynccontextmanager(provider.local_dao)() as holder:
        await init_mapper.init_reservoir_mapper(holder.local_reservoir_replace)


async def init_multi_reservoir_mapper(provider: DbProvider) -> None:
    async with asynccontextmanager(provider.local_dao)() as holder:
        await init_mapper.init_multi_reservoir_mapper(
            holder.local_reservoir_replace
        )


async def init_multi_split_reservoir_mapper(provider: DbProvider) -> None:
    async with asynccontextmanager(provider.local_dao)() as holder:
        await init_mapper.init_multi_split_reservoir_mapper(
            holder.local_reservoir_replace
        )


async def init_layer_mapper(provider: DbProvider) -> None:
    async with asynccontextmanager(provider.local_dao)() as holder:
        await init_mapper.init_layer_mapper(holder.local_layer_replace)


async def init_multi_layer_mapper(provider: DbProvider) -> None:
    async with asynccontextmanager(provider.local_dao)() as holder:
        await init_mapper.init_multi_layer_mapper(holder.local_layer_replace)
