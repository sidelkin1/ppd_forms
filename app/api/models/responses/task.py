from app.api.models.responses.base import BaseResponse
from app.core.models import dto

DatabaseResponse = BaseResponse[dto.TaskDatabase]
ExcelResponse = BaseResponse[dto.TaskExcel]
ReportResponse = BaseResponse[dto.TaskReport]
OilLossResponse = BaseResponse[dto.TaskOilLoss]
FieldsResponse = BaseResponse[dto.TaskFields]
ReservoirsResponse = BaseResponse[dto.TaskReservoirs]
MatrixResponse = BaseResponse[dto.TaskMatrix]
