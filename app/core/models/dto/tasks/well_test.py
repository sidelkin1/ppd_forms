from pydantic import PositiveInt

from app.core.models.dto.tasks.base import TaskBase
from app.core.models.enums import ReportName, TaskId


class TaskWellTest(
    TaskBase, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    name: ReportName
    file: str
    gtm_period: PositiveInt
