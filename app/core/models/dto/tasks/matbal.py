from app.core.models.dto.db.field_list import UneftFieldDB
from app.core.models.dto.db.reservoir_list import UneftReservoirDB
from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import TaskId


class TaskMatbal(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    field: UneftFieldDB
    reservoirs: list[UneftReservoirDB]
    wells: str | None
    measurements: str | None
    alternative: bool
