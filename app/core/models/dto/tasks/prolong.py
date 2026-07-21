from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import Interpolation, TaskId


class TaskProlong(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    expected: str
    actual: str
    interpolations: list[Interpolation]
