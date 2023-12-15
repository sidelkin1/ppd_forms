from contextlib import asynccontextmanager
from typing import Any, cast

from app.api.dependencies.dao.provider import DbProvider
from app.core.config.settings import settings
from app.core.models.schemas import TaskResponse
from app.core.services.entrypoints.arq import registry
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.infrastructure.db.factories.ofm import create_pool as create_ofm_pool
from app.infrastructure.db.models import ofm
from app.initial_data import iniialize_mapper


async def perform_work(ctx: dict[str, Any], response: TaskResponse) -> None:
    await registry[response.task.route_url](response, ctx)


async def startup(ctx: dict[str, Any]) -> None:
    local_pool = create_local_pool(settings)
    ofm_pool = create_ofm_pool(settings) if ofm.setup(settings) else None
    provider = DbProvider(local_pool=local_pool, ofm_pool=ofm_pool)
    ctx["provider"] = provider
    ctx["pool"] = ProcessPoolManager(settings)
    ctx["local_dao"] = asynccontextmanager(provider.local_dao)
    ctx["local_pool_dao"] = asynccontextmanager(provider.local_pool_dao)
    ctx["ofm_local_dao"] = asynccontextmanager(provider.ofm_local_dao)
    ctx["excel_local_dao"] = asynccontextmanager(provider.excel_local_dao)
    await iniialize_mapper(provider)


async def shutdown(ctx: dict[str, Any]) -> None:
    if pool := cast(ProcessPoolManager, ctx.get("pool")):
        pool.close()
    if provider := cast(DbProvider, ctx.get("provider")):
        await provider.dispose()


class WorkerSettings:
    functions = [perform_work]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = settings.redis_settings
    allow_abort_jobs = True
