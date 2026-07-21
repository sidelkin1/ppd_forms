from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import TaskId


class TaskMmb(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    file: str
    alternative: bool
