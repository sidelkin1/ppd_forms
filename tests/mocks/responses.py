from pathlib import Path

from app.core.models.dto import JobStamp, TaskBase
from app.core.models.schemas import TaskResponse


class TaskTest(TaskBase, task_id="test"):
    pass


class TaskTestResponse(TaskResponse[TaskBase]):
    @classmethod
    def test(cls, **kwargs):
        task = TaskTest()
        job_stamp = JobStamp(**kwargs)
        return cls(Path(), task=task, job=job_stamp)
