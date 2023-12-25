from app.core.models.dto.tasks.base import TaskBase
from app.core.models.enums import ExcelTableName, LoadMode, TaskId


class TaskExcel(
    TaskBase, task_id=TaskId.excel, route_fields=["task_id", "table", "mode"]
):
    table: ExcelTableName
    mode: LoadMode
    file: str
