import asyncio
import contextlib
import logging

from app.core.init_db import init_db
from app.core.local_db import get_async_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

get_async_session_context = contextlib.asynccontextmanager(get_async_session)


async def init() -> None:
    async with get_async_session_context() as session:
        await init_db(session)


async def main() -> None:
    logger.info('Создание исходных данных')
    await init()
    logger.info('Исходные данные созданы')


if __name__ == '__main__':
    asyncio.run(main())
