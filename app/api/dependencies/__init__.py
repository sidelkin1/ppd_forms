from arq import ArqRedis
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.dependencies.auth import (
    AuthProvider,
    get_auth_provider,
    get_current_user,
    get_current_user_or_none,
)
from app.api.dependencies.dao.provider import DbProvider, dao_provider
from app.api.dependencies.job import (
    create_job_stamp,
    current_job_provider,
    get_current_job,
    get_job_tracker,
    job_tracker_provider,
    new_job_provider,
)
from app.api.dependencies.redis.provider import RedisProvider, redis_provider
from app.api.dependencies.responses import (
    create_oil_loss_report,
    create_task_database,
    create_task_excel,
    create_task_report,
    get_fields,
    get_job_response,
    get_reservoirs,
    job_response_provider,
    task_database_provider,
    task_excel_provider,
    task_fields_provider,
    task_oil_loss_provider,
    task_report_provider,
    task_reservoirs_provider,
)
from app.api.dependencies.settings import settings_provider
from app.api.dependencies.user import (
    get_file_path,
    get_or_create_directory,
    get_or_create_user_id,
    user_directory_provider,
    user_file_provider,
    user_id_provider,
)
from app.core.config.settings import Settings


def setup(
    app: FastAPI,
    pool: async_sessionmaker[AsyncSession],
    redis: ArqRedis,
    settings: Settings,
) -> None:
    app.dependency_overrides[dao_provider] = DbProvider(
        local_pool=pool
    ).local_dao
    app.dependency_overrides[redis_provider] = RedisProvider(pool=redis).dao
    app.dependency_overrides[settings_provider] = lambda: settings

    auth_provider = AuthProvider(settings)
    app.dependency_overrides[get_current_user] = auth_provider.get_current_user
    app.dependency_overrides[
        get_current_user_or_none
    ] = auth_provider.get_current_user_or_none
    app.dependency_overrides[get_auth_provider] = lambda: auth_provider

    app.dependency_overrides[new_job_provider] = create_job_stamp
    app.dependency_overrides[current_job_provider] = get_current_job
    app.dependency_overrides[job_response_provider] = get_job_response
    app.dependency_overrides[job_tracker_provider] = get_job_tracker

    app.dependency_overrides[user_id_provider] = get_or_create_user_id
    app.dependency_overrides[user_directory_provider] = get_or_create_directory
    app.dependency_overrides[user_file_provider] = get_file_path

    app.dependency_overrides[task_database_provider] = create_task_database
    app.dependency_overrides[task_report_provider] = create_task_report
    app.dependency_overrides[task_excel_provider] = create_task_excel
    app.dependency_overrides[task_oil_loss_provider] = create_oil_loss_report
    app.dependency_overrides[task_fields_provider] = get_fields
    app.dependency_overrides[task_reservoirs_provider] = get_reservoirs
