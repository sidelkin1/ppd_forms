import logging
import os
from typing import Any, cast

import structlog
from arq import cron
from arq.connections import RedisSettings
from dotenv import load_dotenv

from app.common.config.models.paths import Paths
from app.core.config.main import get_app_settings
from app.core.context import WorkerContext
from app.core.models.responses import BaseResponse
from app.core.services.cron.clean_files import cron_clean_files
from app.core.services.cron.refresh_table import (
    cron_refresh_mer,
    cron_refresh_opp,
)
from app.core.services.entrypoints.arq import registry
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.config.main import (
    get_oracle_settings,
    get_postgres_settings,
)
from app.infrastructure.db.models import ofm
from app.infrastructure.files.config.main import get_csv_settings
from app.infrastructure.log.config.main import get_log_settings
from app.infrastructure.log.main import configure_logging
from app.infrastructure.redis.config.main import get_redis_settings
from app.infrastructure.reporters import build_reporters
from app.infrastructure.sessions import Sessions
from app.initial_data import initialize_mapper

load_dotenv()

logger = logging.getLogger(__name__)


async def perform_work(
    ctx: dict[str, Any], response: BaseResponse, log_ctx: dict[str, Any]
) -> Any:
    structlog.contextvars.bind_contextvars(**log_ctx)
    logger.info(
        "Started job", extra={"task": response.task, "job": response.job}
    )
    app: WorkerContext = ctx["app"]
    handler = registry.handler(response.task.route_url)
    return await handler(response, app)


async def startup(ctx: dict[str, Any]) -> None:
    log_config = get_log_settings()
    configure_logging(log_config)
    oracle_config = get_oracle_settings()
    sessions = Sessions.create(
        local_settings=get_postgres_settings(),
        ofm_settings=oracle_config if ofm.setup(oracle_config) else None,
        redis_settings=get_redis_settings(),
    )
    app_config = get_app_settings()
    ctx["app"] = WorkerContext(
        settings=app_config,
        csv=get_csv_settings(),
        paths=Paths(),
        sessions=sessions,
        reporters=build_reporters(sessions),
        process_pool=ProcessPoolManager(max_workers=app_config.max_workers),
    )
    await initialize_mapper(sessions)
    logger.info("worker prepared")


async def shutdown(ctx: dict[str, Any]) -> None:
    if app := cast(WorkerContext | None, ctx.get("app")):
        app.process_pool.close()
        await app.sessions.dispose()
    logger.info("worker closed")


class WorkerSettings:
    functions = [perform_work]
    cron_jobs = [
        cron(
            cron_refresh_opp,
            day=11,
            hour=0,
            minute=0,
            second=0,
            max_tries=3,
        ),
        cron(
            cron_refresh_mer,
            day=11,
            hour=0,
            minute=0,
            second=0,
            max_tries=3,
        ),
        cron(
            cron_clean_files,
            month={3, 6, 9, 12},
            day=1,
            hour=0,
            minute=0,
            second=0,
        ),
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(
        host=cast(str, os.getenv("REDIS_HOST")),
        port=cast(int, os.getenv("REDIS_PORT")),
    )
    allow_abort_jobs = True
    job_timeout = 2500
    keep_result = int(os.getenv("APP_KEEP_RESULT", "86400"))
