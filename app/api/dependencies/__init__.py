from fastapi import FastAPI

from app.api.dependencies.dao.provider import DbProvider, dao_provider
from app.api.dependencies.job import (
    create_job_stamp,
    current_job_provider,
    get_current_job,
    get_job_response,
    get_job_tracker,
    job_response_provider,
    job_tracker_provider,
    new_job_provider,
)
from app.api.dependencies.redis.provider import RedisProvider, redis_provider
from app.api.dependencies.tasks import (
    create_task_database,
    create_task_excel,
    create_task_report,
    task_database_provider,
    task_excel_provider,
    task_report_provider,
)
from app.api.dependencies.user import (
    get_or_create_directory,
    get_or_create_path,
    get_or_create_user_id,
    user_directory_provider,
    user_file_provider,
    user_id_provider,
)


def setup(app: FastAPI):
    app.dependency_overrides[dao_provider] = DbProvider(
        local_pool=app.state.pool
    ).local_dao
    app.dependency_overrides[redis_provider] = RedisProvider(
        pool=app.state.redis
    ).dao

    app.dependency_overrides[new_job_provider] = create_job_stamp
    app.dependency_overrides[current_job_provider] = get_current_job
    app.dependency_overrides[job_response_provider] = get_job_response
    app.dependency_overrides[job_tracker_provider] = get_job_tracker

    app.dependency_overrides[user_id_provider] = get_or_create_user_id
    app.dependency_overrides[user_directory_provider] = get_or_create_directory
    app.dependency_overrides[user_file_provider] = get_or_create_path

    app.dependency_overrides[task_database_provider] = create_task_database
    app.dependency_overrides[task_report_provider] = create_task_report
    app.dependency_overrides[task_excel_provider] = create_task_excel
