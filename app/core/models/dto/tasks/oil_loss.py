from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import LossMode, TaskId


class TaskOilLoss(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name", "mode"]
):
    mode: LossMode
