import logging
from pathlib import Path

import structlog

from app.core.services.reports.log.bound import BoundLogger
from app.core.services.reports.log.config import configure_logging


class LogContext:
    def __init__(self, name: str, path: Path) -> None:
        self.logger = configure_logging(name, path)

    def __enter__(self) -> BoundLogger:
        return self.open()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def open(self) -> BoundLogger:
        return BoundLogger(
            self.logger,
            processors=(
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.stdlib.render_to_log_kwargs,
            ),
            context=structlog.contextvars.get_contextvars(),
        )

    def close(self) -> None:
        logging.root.manager.loggerDict.pop(self.logger.name, None)
