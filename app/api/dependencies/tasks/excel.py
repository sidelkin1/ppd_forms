from typing import Annotated

from fastapi import Depends

from app.core.models.dto import TaskExcel
from app.core.models.enums import ExcelTableName, LoadMode
from app.core.models.schemas import ExcelPath


def task_excel_provider() -> TaskExcel:
    raise NotImplementedError


async def create_task_excel(
    table: ExcelTableName,
    mode: LoadMode,
    path: ExcelPath,
) -> TaskExcel:
    return TaskExcel(table=table.value, mode=mode.value, file=path.file)


TaskExcelDep = Annotated[TaskExcel, Depends(task_excel_provider)]
