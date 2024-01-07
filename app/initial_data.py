import asyncio
import logging

from app.api.dependencies.dao.provider import DbProvider
from app.core.config.settings import Settings, get_settings
from app.core.services.entrypoints import db, mapper
from app.infrastructure.db.factories.local import create_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_replace(provider: DbProvider, settings: Settings) -> None:
    await asyncio.gather(
        db.init_field_replace(provider, settings),
        db.init_reservoir_replace(provider, settings),
        db.init_layer_replace(provider, settings),
    )


async def initialize_mapper(provider: DbProvider) -> None:
    await asyncio.gather(
        mapper.init_field_mapper(provider),
        mapper.init_reservoir_mapper(provider),
        mapper.init_multi_reservoir_mapper(provider),
        mapper.init_multi_split_reservoir_mapper(provider),
        mapper.init_layer_mapper(provider),
        mapper.init_multi_layer_mapper(provider),
    )


async def initialize_main(provider: DbProvider, settings: Settings) -> None:
    await asyncio.gather(
        # db.init_monthly_report(provider, settings),
        db.init_well_profile(provider, settings),
    )


async def main() -> None:
    try:
        logger.info("Создание исходных данных")
        settings = get_settings()
        pool = create_pool(settings)
        provider = DbProvider(local_pool=pool)
        await initialize_replace(provider, settings)
        await initialize_mapper(provider)
        await initialize_main(provider, settings)
        logger.info("Исходные данные созданы")
    finally:
        await provider.dispose()


if __name__ == "__main__":
    asyncio.run(main())
