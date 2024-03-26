import logging
import os
from contextlib import asynccontextmanager
from typing import Any, cast

from arq.connections import RedisSettings
from dotenv import load_dotenv

from app.api.dependencies.db import DbProvider
from app.api.dependencies.path import PathProvider
from app.core.config.settings import get_settings
from app.core.models.schemas import BaseResponse
from app.core.services.entrypoints.arq import registry
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.infrastructure.db.factories.ofm import create_pool as create_ofm_pool
from app.infrastructure.db.models import ofm
from app.infrastructure.log.main import configure_logging
from app.initial_data import initialize_mapper

load_dotenv()

logger = logging.getLogger(__name__)


async def perform_work(ctx: dict[str, Any], response: BaseResponse) -> None:
    return await registry[response.task.route_url](response, ctx)


async def startup(ctx: dict[str, Any]) -> None:
    settings = get_settings()
    configure_logging(settings)
    local_pool = create_local_pool(settings)
    ofm_pool = create_ofm_pool(settings) if ofm.setup(settings) else None
    provider = DbProvider(local_pool=local_pool, ofm_pool=ofm_pool)
    ctx["settings"] = settings
    ctx["provider"] = provider
    ctx["path_provider"] = PathProvider(settings)
    ctx["pool"] = ProcessPoolManager(settings)
    ctx["local_dao"] = asynccontextmanager(provider.local_dao)
    ctx["ofm_dao"] = asynccontextmanager(provider.ofm_dao)
    ctx["local_pool_dao"] = asynccontextmanager(provider.local_pool_dao)
    ctx["ofm_local_dao"] = asynccontextmanager(provider.ofm_local_dao)
    ctx["ofm_pool_dao"] = asynccontextmanager(provider.ofm_pool_dao)
    ctx["file_local_dao"] = asynccontextmanager(provider.file_local_dao)
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
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(
        host=cast(str, os.getenv("REDIS_HOST")),
        port=cast(int, os.getenv("REDIS_PORT")),
    )
    allow_abort_jobs = True
