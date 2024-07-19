import logging.handlers

import structlog
from sqlalchemy import log as sa_log
from structlog.processors import CallsiteParameter, CallsiteParameterAdder

from app.infrastructure.log.config.main import LogSettings
from app.infrastructure.log.processors import get_render_processor

logger = logging.getLogger(__name__)


def configure_logging(settings: LogSettings) -> None:
    # Mute SQLAlchemy default logger handler
    sa_log._add_default_handler = lambda _: None  # type: ignore

    # Mute arq default logger handler
    arq_logger = logging.getLogger("arq")
    arq_logger.handlers.clear()
    arq_logger.propagate = True

    common_processors = (
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.ExtraAdder(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.contextvars.merge_contextvars,
        CallsiteParameterAdder(
            (
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.LINENO,
            )
        ),
    )
    if settings.render_json_logs:
        common_processors += (  # type: ignore
            structlog.processors.dict_tracebacks,
        )
    structlog_processors = (
        structlog.processors.StackInfoRenderer(),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    )
    logging_processors = (
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
    )
    logging_console_processors = (
        *logging_processors,
        get_render_processor(
            render_json_logs=settings.render_json_logs, colors=True
        ),
    )
    logging_file_processors = (
        *logging_processors,
        get_render_processor(
            render_json_logs=settings.render_json_logs, colors=False
        ),
    )

    handler = logging.StreamHandler()
    handler.set_name("default")
    handler.setLevel(settings.log_level)
    console_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=common_processors,
        processors=logging_console_processors,
    )
    handler.setFormatter(console_formatter)

    handlers: list[logging.Handler] = [handler]
    if settings.log_path:
        log_path = (
            settings.log_path / "logs.log"
            if settings.log_path.is_dir()
            else settings.log_path
        )

        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            backupCount=settings.log_backup_count,
            maxBytes=settings.log_max_bytes,
            encoding="utf8",
        )
        file_handler.set_name("file")
        file_handler.setLevel(settings.log_level)
        file_formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=common_processors,
            processors=logging_file_processors,
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    logging.basicConfig(
        handlers=handlers, level=settings.log_level, force=True
    )
    structlog.configure(
        processors=common_processors + structlog_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logger.info("Logging configured successfully")
