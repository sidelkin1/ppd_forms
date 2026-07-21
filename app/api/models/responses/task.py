from typing import Self, TypeVar

from pydantic import model_validator

from app.api.models.responses.base import BaseResponse
from app.core.models import dto
from app.core.models.dto.tasks.report import TaskReport

RT = TypeVar("RT", bound=TaskReport)


class ReportResponse(BaseResponse[RT]):
    @model_validator(mode="after")
    def propagate_prefix(self) -> Self:
        self.job.prefix = self.task.filename_prefix
        return self


ProfileResponse = ReportResponse[dto.TaskProfile]
OppPerYearResponse = ReportResponse[dto.TaskOppPerYear]
InjLossResponse = ReportResponse[dto.TaskInjLoss]
OilLossResponse = ReportResponse[dto.TaskOilLoss]
MatrixResponse = ReportResponse[dto.TaskMatrix]
FnvResponse = ReportResponse[dto.TaskFNV]
MatbalResponse = ReportResponse[dto.TaskMatbal]
ProlongResponse = ReportResponse[dto.TaskProlong]
MmbResponse = ReportResponse[dto.TaskMmb]
CompensationResponse = ReportResponse[dto.TaskCompensation]
WellTestResponse = ReportResponse[dto.TaskWellTest]
OwcRespResponse = ReportResponse[dto.TaskOwcResp]

DatabaseResponse = BaseResponse[dto.TaskDatabase]
ExcelResponse = BaseResponse[dto.TaskExcel]
FieldsResponse = BaseResponse[dto.TaskFields]
ReservoirsResponse = BaseResponse[dto.TaskReservoirs]
WellsResponse = BaseResponse[dto.TaskWells]
