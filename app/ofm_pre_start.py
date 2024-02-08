import logging

from sqlalchemy import text
from tenacity import (
    after_log,
    before_log,
    retry,
    stop_after_attempt,
    wait_fixed,
)

from app.core.config.settings import get_settings
from app.infrastructure.db.factories.ofm import create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 3
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    engine = None
    try:
        settings = get_settings()
        engine = create_engine(settings)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM DUAL"))
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        if engine is not None:
            engine.dispose()


def main() -> None:
    logger.info("Initializing service")
    init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
