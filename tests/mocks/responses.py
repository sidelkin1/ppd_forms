from app.core.models.dto import JobStamp, TaskBase
from app.core.models.schemas import BaseResponse


class TaskTest(TaskBase, task_id="test"):
    pass


class TaskTestResponse(BaseResponse[TaskBase]):
    @classmethod
    def test(cls, **kwargs):
        task = TaskTest()
        job_stamp = JobStamp(**kwargs)
        return cls(task=task, job=job_stamp)
