from app.core.models.dto import TaskFields, TaskReservoirs
from app.core.models.schemas.responses.task import TaskResponse


class FieldsResponse(TaskResponse[TaskFields]):
    pass


class ReservoirsResponse(TaskResponse[TaskReservoirs]):
    pass
