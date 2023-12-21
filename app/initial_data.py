import asyncio
import logging

from app.api.dependencies.dao.provider import DbProvider
from app.core.config.settings import settings
from app.core.services.entrypoints import db, mapper
from app.infrastructure.db.factories.local import create_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_replace(provider: DbProvider) -> None:
    await asyncio.gather(
        db.init_field_replace(provider),
        db.init_reservoir_replace(provider),
        db.init_layer_replace(provider),
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


async def initialize_main(provider: DbProvider) -> None:
    await asyncio.gather(
        # db.init_monthly_report(provider),
        db.init_well_profile(provider),
    )


async def main() -> None:
    try:
        logger.info("Создание исходных данных")
        pool = create_pool(settings)
        provider = DbProvider(local_pool=pool)
        await initialize_replace(provider)
        await initialize_mapper(provider)
        await initialize_main(provider)
        logger.info("Исходные данные созданы")
    finally:
        await provider.dispose()


if __name__ == "__main__":
    asyncio.run(main())
