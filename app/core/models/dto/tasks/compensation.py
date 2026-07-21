from datetime import date

from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import TaskId


class TaskCompensation(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    on_date: date
