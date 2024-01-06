from app.core.models.dto import JobStamp, TaskBase
from app.core.models.enums import JobStatus
from app.core.models.schemas import TaskResponse


class TaskTest(TaskBase, task_id="test"):
    pass


class TaskTestResponse(TaskResponse[TaskBase]):
    @classmethod
    def test(cls):
        task = TaskTest()
        job_stamp = JobStamp()
        return cls(task=task, job=job_stamp)

    @classmethod
    def test_ok(cls):
        task = TaskTest()
        job_stamp = JobStamp(
            status=JobStatus.completed, message="Job is completed"
        )
        return cls(task=task, job=job_stamp)

    @classmethod
    def test_error(cls):
        task = TaskTest()
        job_stamp = JobStamp(status=JobStatus.error, message="Error!")
        return TaskResponse(task=task, job=job_stamp)
