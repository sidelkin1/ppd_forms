from typing import Annotated

from fastapi import Depends

from app.api.dependencies.job import NewJobDep
from app.api.dependencies.settings import SettingsDep
from app.core.models.dto import TaskOilLoss
from app.core.models.enums import LossMode, ReportName
from app.core.models.schemas import DateRange, OilLossResponse


def task_oil_loss_provider() -> TaskOilLoss:
    raise NotImplementedError


async def create_oil_loss_report(
    mode: LossMode,
    date_range: DateRange,
    job_stamp: NewJobDep,
    settings: SettingsDep,
) -> OilLossResponse:
    task = TaskOilLoss(
        name=ReportName.oil_loss,
        mode=mode,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )
    return OilLossResponse(
        _file_dir=settings.file_dir, task=task, job=job_stamp
    )


OilLossResponseDep = Annotated[
    OilLossResponse, Depends(task_oil_loss_provider)
]
