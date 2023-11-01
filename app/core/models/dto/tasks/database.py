from datetime import date

from app.core.models.dto.tasks.base import TaskBase
from app.core.models.enums import LoadMode, OfmTableName, TaskId


class TaskDatabase(
    TaskBase,
    task_id=TaskId.database,
    route_fields=["task_id", "table", "mode"],
):
    table: OfmTableName
    mode: LoadMode
    date_from: date
    date_to: date
