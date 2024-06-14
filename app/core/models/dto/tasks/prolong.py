from app.core.models.dto.tasks.base import TaskBase
from app.core.models.enums import Interpolation, ReportName, TaskId


class TaskProlong(
    TaskBase, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    name: ReportName
    expected: str
    actual: str
    interpolation: Interpolation
