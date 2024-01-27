import logging.config
from pathlib import Path

import yaml
from sqlalchemy import log as sa_log

logger = logging.getLogger(__name__)


def setup_logging(path: Path):
    # monkey patching logging sqlalchemy
    sa_log._add_default_handler = lambda _: None  # type: ignore[assignment]
    try:
        with path.open("r") as f:
            logging_config = yaml.safe_load(f)
        logging.config.dictConfig(logging_config)
        logger.info("Logging configured successfully")
    except IOError:
        logging.basicConfig(level=logging.DEBUG)
        logger.warning("logging config file not found, use basic config")
