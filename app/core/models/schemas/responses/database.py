from app.core.models.dto import TaskDatabase
from app.core.models.schemas.responses.task import TaskResponse


class DatabaseResponse(TaskResponse[TaskDatabase]):
    pass
