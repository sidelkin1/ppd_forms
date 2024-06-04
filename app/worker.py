import logging
import os
from contextlib import asynccontextmanager
from typing import Any, cast

import structlog
from arq import cron
from arq.connections import RedisSettings
from dotenv import load_dotenv

from app.api.dependencies.db import DbProvider
from app.api.dependencies.path import PathProvider
from app.api.models.responses import BaseResponse
from app.core.config.main import get_app_settings
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
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.infrastructure.db.factories.ofm import create_pool as create_ofm_pool
from app.infrastructure.db.models import ofm
from app.infrastructure.files.config.main import get_csv_settings
from app.infrastructure.files.config.models.paths import Paths
from app.infrastructure.log.config.main import get_log_settings
from app.infrastructure.log.main import configure_logging
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
    return await registry[response.task.route_url](response, ctx)


async def startup(ctx: dict[str, Any]) -> None:
    log_config = get_log_settings()
    configure_logging(log_config)
    postgres_config = get_postgres_settings()
    local_pool = create_local_pool(postgres_config)
    oracle_config = get_oracle_settings()
    ofm_pool = (
        create_ofm_pool(oracle_config) if ofm.setup(oracle_config) else None
    )
    provider = DbProvider(local_pool=local_pool, ofm_pool=ofm_pool)
    paths = Paths()
    app_config = get_app_settings()
    ctx["app_config"] = app_config
    ctx["csv_config"] = get_csv_settings()
    ctx["provider"] = provider
    ctx["path_provider"] = PathProvider(paths)
    ctx["pool"] = ProcessPoolManager(max_workers=app_config.max_workers)
    ctx["local_dao"] = asynccontextmanager(provider.local_dao)
    ctx["ofm_dao"] = asynccontextmanager(provider.ofm_dao)
    ctx["ofm_local_dao"] = asynccontextmanager(provider.ofm_local_dao)
    await initialize_mapper(provider)
    logger.info("worker prepared")


async def shutdown(ctx: dict[str, Any]) -> None:
    if pool := cast(ProcessPoolManager, ctx.get("pool")):
        pool.close()
    if provider := cast(DbProvider, ctx.get("provider")):
        await provider.dispose()
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
