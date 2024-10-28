import asyncio
import logging

from app.common.config.models.paths import Paths
from app.core.services.entrypoints import db, mapper
from app.infrastructure.db.config.main import get_postgres_settings
from app.infrastructure.db.factories.local import create_pool
from app.infrastructure.provider import DbProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_replace(
    provider: DbProvider,
    paths: Paths,
) -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(db.init_field_replace(provider, paths))
        tg.create_task(db.init_reservoir_replace(provider, paths))
        tg.create_task(db.init_layer_replace(provider, paths))
        tg.create_task(db.init_gtm_replace(provider, paths))


async def initialize_mapper(provider: DbProvider) -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(mapper.init_field_mapper(provider))
        tg.create_task(mapper.init_reservoir_mapper(provider))
        tg.create_task(mapper.init_multi_reservoir_mapper(provider))
        tg.create_task(mapper.init_multi_split_reservoir_mapper(provider))
        tg.create_task(mapper.init_layer_mapper(provider))
        tg.create_task(mapper.init_multi_layer_mapper(provider))
        tg.create_task(mapper.init_gtm_mapper(provider))


async def initialize_main(provider: DbProvider, paths: Paths) -> None:
    async with asyncio.TaskGroup() as tg:
        # tg.create_task(db.init_monthly_report(provider, settings))
        tg.create_task(db.init_well_profile(provider, paths))
        tg.create_task(db.init_well_test(provider, paths))


async def initialize_all(provider: DbProvider, paths: Paths) -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(db.init_monthly_report(provider, paths))
        tg.create_task(db.init_well_profile(provider, paths))
        tg.create_task(db.init_inj_well_database(provider, paths))
        tg.create_task(db.init_neighborhood(provider, paths))
        tg.create_task(db.init_new_strategy_inj(provider, paths))
        tg.create_task(db.init_new_strategy_oil(provider, paths))


async def main() -> None:  # pragma: no cover
    try:
        logger.info("Создание исходных данных")
        postgres_config = get_postgres_settings()
        pool = create_pool(postgres_config)
        provider = DbProvider(local_pool=pool)
        paths = Paths()
        await initialize_replace(provider, paths)
        await initialize_mapper(provider)
        await initialize_main(provider, paths)
        logger.info("Исходные данные созданы")
    finally:
        await provider.dispose()


if __name__ == "__main__":
    asyncio.run(main())
