from typing import Self, TypeVar

from pydantic import model_validator

from app.core.models.dto.responses.base import BaseResponse
from app.core.models.dto.tasks.compensation import TaskCompensation
from app.core.models.dto.tasks.database import TaskDatabase
from app.core.models.dto.tasks.excel import TaskExcel
from app.core.models.dto.tasks.fnv import TaskFNV
from app.core.models.dto.tasks.inj_loss import TaskInjLoss
from app.core.models.dto.tasks.matbal import TaskMatbal
from app.core.models.dto.tasks.matrix import TaskMatrix
from app.core.models.dto.tasks.mmb import TaskMmb
from app.core.models.dto.tasks.oil_loss import TaskOilLoss
from app.core.models.dto.tasks.opp_per_year import TaskOppPerYear
from app.core.models.dto.tasks.owc_resp import TaskOwcResp
from app.core.models.dto.tasks.profile import TaskProfile
from app.core.models.dto.tasks.prolong import TaskProlong
from app.core.models.dto.tasks.report import TaskReport
from app.core.models.dto.tasks.uneft import (
    TaskFields,
    TaskReservoirs,
    TaskWells,
)
from app.core.models.dto.tasks.utils import TaskUtils
from app.core.models.dto.tasks.well_test import TaskWellTest

RT = TypeVar("RT", bound=TaskReport)


class ReportResponse(BaseResponse[RT]):
    @model_validator(mode="after")
    def propagate_prefix(self) -> Self:
        self.job.prefix = self.task.filename_prefix
        return self


ProfileResponse = ReportResponse[TaskProfile]
OppPerYearResponse = ReportResponse[TaskOppPerYear]
InjLossResponse = ReportResponse[TaskInjLoss]
OilLossResponse = ReportResponse[TaskOilLoss]
MatrixResponse = ReportResponse[TaskMatrix]
FnvResponse = ReportResponse[TaskFNV]
MatbalResponse = ReportResponse[TaskMatbal]
ProlongResponse = ReportResponse[TaskProlong]
MmbResponse = ReportResponse[TaskMmb]
CompensationResponse = ReportResponse[TaskCompensation]
WellTestResponse = ReportResponse[TaskWellTest]
OwcRespResponse = ReportResponse[TaskOwcResp]

DatabaseResponse = BaseResponse[TaskDatabase]
ExcelResponse = BaseResponse[TaskExcel]
FieldsResponse = BaseResponse[TaskFields]
ReservoirsResponse = BaseResponse[TaskReservoirs]
WellsResponse = BaseResponse[TaskWells]
UtilsResponse = BaseResponse[TaskUtils]
