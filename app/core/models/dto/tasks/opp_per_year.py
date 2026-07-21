from datetime import date

from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import TaskId


class TaskOppPerYear(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    date_from: date
    date_to: date
