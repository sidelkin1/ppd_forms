from typing import Annotated

from fastapi import Depends

from app.api.dependencies.job import NewJobDep
from app.api.dependencies.settings import SettingsDep
from app.core.models.dto import TaskReport
from app.core.models.enums import ReportName
from app.core.models.schemas import DateRange, ReportResponse


def task_report_provider() -> TaskReport:
    raise NotImplementedError


async def create_task_report(
    name: ReportName,
    date_range: DateRange,
    job_stamp: NewJobDep,
    settings: SettingsDep,
) -> ReportResponse:
    task = TaskReport(
        name=name,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )
    return ReportResponse(
        _file_dir=settings.file_dir, task=task, job=job_stamp
    )


ReportResponseDep = Annotated[ReportResponse, Depends(task_report_provider)]
