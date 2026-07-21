from pydantic import NonNegativeFloat

from app.core.models.dto.db.field_list import UneftFieldDB
from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import TaskId


class TaskFNV(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    fields: list[UneftFieldDB]
    min_radius: NonNegativeFloat
    alternative: bool
    max_fields: int
