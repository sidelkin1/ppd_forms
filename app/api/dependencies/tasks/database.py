from typing import Annotated

from fastapi import Depends

from app.core.models.dto import TaskDatabase
from app.core.models.enums import LoadMode, OfmTableName
from app.core.models.schemas import DateRange


def task_database_provider() -> TaskDatabase:
    raise NotImplementedError


async def create_task_database(
    table: OfmTableName, mode: LoadMode, date_range: DateRange
) -> TaskDatabase:
    return TaskDatabase(
        table=table.value, mode=mode.value, **date_range.model_dump()
    )


TaskDatabaseDep = Annotated[TaskDatabase, Depends(task_database_provider)]
