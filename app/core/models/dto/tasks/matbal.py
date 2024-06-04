from app.core.models.dto.db.field_list import UneftFieldDB
from app.core.models.dto.db.reservoir_list import UneftReservoirDB
from app.core.models.dto.tasks.base import TaskBase
from app.core.models.enums import ReportName, TaskId


class TaskMatbal(
    TaskBase, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    name: ReportName
    field: UneftFieldDB
    reservoirs: list[UneftReservoirDB]
    wells: str | None = None
    measurements: str | None = None
    alternative: bool
