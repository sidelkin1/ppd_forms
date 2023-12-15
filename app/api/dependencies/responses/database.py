from typing import Annotated

from fastapi import Depends

from app.api.dependencies.job import NewJobDep
from app.core.models.dto import TaskDatabase
from app.core.models.enums import LoadMode, OfmTableName
from app.core.models.schemas import DatabaseResponse, DateRange


def task_database_provider() -> TaskDatabase:
    raise NotImplementedError


async def create_task_database(
    table: OfmTableName,
    mode: LoadMode,
    date_range: DateRange,
    job_stamp: NewJobDep,
) -> DatabaseResponse:
    task = TaskDatabase(
        table=table,
        mode=mode,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )
    return DatabaseResponse(task=task, job=job_stamp)


DatabaseResponseDep = Annotated[
    DatabaseResponse, Depends(task_database_provider)
]
