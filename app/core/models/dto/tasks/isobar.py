from datetime import date

from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import TaskId


class TaskIsobar(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    file: str
    previous_date: date
    on_date: date
    stock_date: date
