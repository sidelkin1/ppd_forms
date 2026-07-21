from app.core.models.dto.tasks.base import TaskBase
from app.core.models.enums import ReportName, TaskId


class TaskReport(
    TaskBase, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    name: ReportName

    @property
    def filename_prefix(self) -> str:
        return self.name.value
