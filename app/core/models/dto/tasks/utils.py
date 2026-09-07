from app.core.models.dto.tasks.base import TaskBase
from app.core.models.enums import LoadMode, TaskId, UtilsTableName


class TaskUtils(
    TaskBase,
    task_id=TaskId.utils,
    route_fields=["task_id", "table", "mode"],
):
    table: UtilsTableName
    mode: LoadMode
    file: str
