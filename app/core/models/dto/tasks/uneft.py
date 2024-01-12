from app.core.models.dto.tasks.base import TaskBase
from app.core.models.enums import TaskId, UneftAssets


class TaskUneft(
    TaskBase, task_id=TaskId.uneft, route_fields=["task_id", "assets"]
):
    assets: UneftAssets


class TaskFields(
    TaskUneft, task_id=TaskId.uneft, route_fields=["task_id", "assets"]
):
    pass


class TaskReservoirs(
    TaskUneft, task_id=TaskId.uneft, route_fields=["task_id", "assets"]
):
    field_id: int
