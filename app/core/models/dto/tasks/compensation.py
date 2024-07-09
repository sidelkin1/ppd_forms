from datetime import date

from app.core.models.dto.tasks.base import TaskBase
from app.core.models.enums import ReportName, TaskId


class TaskCompensation(
    TaskBase, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    name: ReportName
    on_date: date
