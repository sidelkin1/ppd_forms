from datetime import date

from pydantic import PositiveInt

from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import ExcludeGTM, TaskId


class TaskMatrix(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    date_from: date
    date_to: date
    base_period: PositiveInt
    pred_period: PositiveInt | None
    excludes: list[ExcludeGTM]
    on_date: date | None
    wells: str | None
