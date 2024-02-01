from app.core.models import dto
from app.core.models.schemas.responses.base import BaseResponse

DatabaseResponse = BaseResponse[dto.TaskDatabase]
ExcelResponse = BaseResponse[dto.TaskExcel]
ReportResponse = BaseResponse[dto.TaskReport]
OilLossResponse = BaseResponse[dto.TaskOilLoss]
FieldsResponse = BaseResponse[dto.TaskFields]
ReservoirsResponse = BaseResponse[dto.TaskReservoirs]
