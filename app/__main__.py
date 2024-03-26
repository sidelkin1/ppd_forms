import asyncio
import logging

from app.core.config.settings import get_settings
from app.infrastructure.log.main import configure_logging
from app.main import init_api, init_mapper, run_api

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()
    configure_logging(settings)
    logger.info("Launch app")
    await init_mapper(settings)
    app = init_api(settings)
    await run_api(app, settings)


if __name__ == "__main__":
    asyncio.run(main())
