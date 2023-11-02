from typing import Annotated

from fastapi import Depends

from app.core.models.dto import TaskReport
from app.core.models.enums import ReportName
from app.core.models.schemas import DateRange


def task_report_provider() -> TaskReport:
    raise NotImplementedError


async def create_task_report(
    name: ReportName, date_range: DateRange
) -> TaskReport:
    return TaskReport(name=name, **date_range.model_dump())


TaskReportDep = Annotated[TaskReport, Depends(task_report_provider)]
