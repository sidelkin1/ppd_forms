import asyncio
import logging

from app.common.config.models.paths import Paths
from app.core.services.entrypoints import db, mapper
from app.infrastructure.db.config.main import get_postgres_settings
from app.infrastructure.sessions import Sessions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_replace(sessions: Sessions, paths: Paths) -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(db.init_field_replace(sessions, paths))
        tg.create_task(db.init_reservoir_replace(sessions, paths))
        tg.create_task(db.init_layer_replace(sessions, paths))
        tg.create_task(db.init_gtm_replace(sessions, paths))


async def initialize_mapper(sessions: Sessions) -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(mapper.init_field_mapper(sessions))
        tg.create_task(mapper.init_reservoir_mapper(sessions))
        tg.create_task(mapper.init_multi_reservoir_mapper(sessions))
        tg.create_task(mapper.init_multi_split_reservoir_mapper(sessions))
        tg.create_task(mapper.init_layer_mapper(sessions))
        tg.create_task(mapper.init_gtm_mapper(sessions))
        tg.create_task(mapper.init_multi_layer_mapper(sessions))


async def initialize_main(sessions: Sessions, paths: Paths) -> None:
    async with asyncio.TaskGroup() as tg:
        # tg.create_task(db.init_monthly_report(sessions, paths))
        tg.create_task(db.init_well_profile(sessions, paths))
        tg.create_task(db.init_well_test(sessions, paths))


async def initialize_all(sessions: Sessions, paths: Paths) -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(db.init_monthly_report(sessions, paths))
        tg.create_task(db.init_well_profile(sessions, paths))
        tg.create_task(db.init_inj_well_database(sessions, paths))
        tg.create_task(db.init_neighborhood(sessions, paths))
        tg.create_task(db.init_new_strategy_inj(sessions, paths))
        tg.create_task(db.init_new_strategy_oil(sessions, paths))


async def main() -> None:  # pragma: no cover
    try:
        logger.info("Создание исходных данных")
        sessions = Sessions.create(local_settings=get_postgres_settings())
        paths = Paths()
        await initialize_replace(sessions, paths)
        await initialize_mapper(sessions)
        await initialize_main(sessions, paths)
        logger.info("Исходные данные созданы")
    finally:
        await sessions.dispose()


if __name__ == "__main__":
    asyncio.run(main())
