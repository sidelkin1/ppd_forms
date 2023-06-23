import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.init_db import (init_field_replace, init_layer_replace,
                              init_profile, init_reservoir_replace)
from app.core.local_db import get_async_session
from app.unify.init_mapper import (init_field_mapper, init_layer_mapper,
                                   init_multi_layer_mapper,
                                   init_multi_reservoir_mapper,
                                   init_reservoir_mapper)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

get_async_session_context = asynccontextmanager(get_async_session)


async def init(func: Callable[[AsyncSession], None]) -> None:
    async with get_async_session_context() as session:
        await func(session)


async def init_replace():
    await asyncio.gather(*map(init, (
        init_field_replace,
        init_reservoir_replace,
        init_layer_replace,
    )))


async def init_mapper():
    await asyncio.gather(*map(init, (
        init_field_mapper,
        init_reservoir_mapper,
        init_multi_reservoir_mapper,
        init_layer_mapper,
        init_multi_layer_mapper,
    )))


async def main() -> None:
    logger.info('Создание исходных данных')
    await init_replace()
    await init_mapper()
    await init(init_profile)
    logger.info('Исходные данные созданы')


if __name__ == '__main__':
    asyncio.run(main())
