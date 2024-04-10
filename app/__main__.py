import asyncio
import logging

from app.infrastructure.db.config.main import get_postgres_settings
from app.infrastructure.log.config.main import get_log_settings
from app.infrastructure.log.main import configure_logging
from app.main import init_api, init_mapper, run_api

logger = logging.getLogger(__name__)


async def main() -> None:
    log_config = get_log_settings()
    configure_logging(log_config)
    logger.info("Launch app")
    postgres_config = get_postgres_settings()
    await init_mapper(postgres_config)
    app = init_api()
    await run_api(app, log_config.log_level)


if __name__ == "__main__":
    asyncio.run(main())
