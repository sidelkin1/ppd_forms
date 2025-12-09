from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import LossMode, TaskId


class TaskInjLoss(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name", "mode"]
):
    mode: LossMode
    neighbs_from_ns_ppd: bool
