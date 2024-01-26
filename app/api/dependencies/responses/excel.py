from typing import Annotated

from fastapi import Depends

from app.api.dependencies.job import NewJobDep
from app.api.dependencies.settings import SettingsDep
from app.core.models.dto import TaskExcel
from app.core.models.enums import ExcelTableName, LoadMode
from app.core.models.schemas import ExcelPath, ExcelResponse


def task_excel_provider() -> TaskExcel:
    raise NotImplementedError


async def create_task_excel(
    table: ExcelTableName,
    mode: LoadMode,
    path: ExcelPath,
    job_stamp: NewJobDep,
    settings: SettingsDep,
) -> ExcelResponse:
    task = TaskExcel(table=table, mode=mode, file=path.file)
    return ExcelResponse(_file_dir=settings.file_dir, task=task, job=job_stamp)


ExcelResponseDep = Annotated[ExcelResponse, Depends(task_excel_provider)]
