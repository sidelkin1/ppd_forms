from app.core.models.dto.tasks.base import TaskBase


class TaskTest(TaskBase, task_id="test"):
    pass


a = TaskTest()
print(a)
