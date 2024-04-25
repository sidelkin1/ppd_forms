from pydantic import NonNegativeFloat

from app.core.models.dto.db.field_list import UneftFieldDB
from app.core.models.dto.tasks.base import TaskBase
from app.core.models.enums import ReportName, TaskId


class TaskFNV(
    TaskBase, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    name: ReportName
    field: UneftFieldDB
    min_radius: NonNegativeFloat
    alternative: bool
