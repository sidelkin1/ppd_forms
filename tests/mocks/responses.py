from typing import Self

from app.api.models.responses import BaseResponse
from app.core.models.dto import JobStamp, TaskBase


class TaskTest(TaskBase, task_id="test"):
    pass


class TaskTestResponse(BaseResponse[TaskBase]):
    @classmethod
    def test(cls, **kwargs) -> Self:
        task = TaskTest()
        job_stamp = JobStamp(**kwargs)
        return cls(task=task, job=job_stamp)
