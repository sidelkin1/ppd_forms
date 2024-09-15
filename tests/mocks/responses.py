from typing import Self

from app.api.models.responses import BaseResponse
from app.core.models.dto import JobStamp, TaskBase
from app.core.models.enums import TaskId


class TaskTest(TaskBase, task_id=TaskId.report):
    pass


class TaskFoo(TaskBase, task_id=TaskId.database):
    pass


class TaskBar(TaskBase, task_id=TaskId.excel):
    pass


class TaskTestResponse(BaseResponse[TaskBase]):
    @classmethod
    def test(cls, **kwargs) -> Self:
        task = TaskTest()
        job_stamp = JobStamp(**kwargs)
        return cls(task=task, job=job_stamp)

    @classmethod
    def foo(cls, **kwargs) -> Self:
        task = TaskFoo()
        job_stamp = JobStamp(**kwargs)
        return cls(task=task, job=job_stamp)

    @classmethod
    def bar(cls, **kwargs) -> Self:
        task = TaskBar()
        job_stamp = JobStamp(**kwargs)
        return cls(task=task, job=job_stamp)
