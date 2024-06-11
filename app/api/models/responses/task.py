from app.api.models.responses.base import BaseResponse
from app.core.models import dto

DatabaseResponse = BaseResponse[dto.TaskDatabase]
ExcelResponse = BaseResponse[dto.TaskExcel]
ReportResponse = BaseResponse[dto.TaskReport]
InjLossResponse = BaseResponse[dto.TaskInjLoss]
OilLossResponse = BaseResponse[dto.TaskOilLoss]
FieldsResponse = BaseResponse[dto.TaskFields]
ReservoirsResponse = BaseResponse[dto.TaskReservoirs]
WellsResponse = BaseResponse[dto.TaskWells]
MatrixResponse = BaseResponse[dto.TaskMatrix]
FnvResponse = BaseResponse[dto.TaskFNV]
MatbalResponse = BaseResponse[dto.TaskMatbal]
ProlongResponse = BaseResponse[dto.TaskProlong]
