import pytest

from app.core.models.dto import JobStamp, TaskBase
from app.core.models.enums import JobStatus
from app.core.models.schemas import TaskResponse


class TaskTest(TaskBase, task_id="test"):
    pass


@pytest.fixture(scope="session")
def test_response() -> TaskResponse[TaskTest]:
    task = TaskTest()
    job_stamp = JobStamp()
    return TaskResponse(task=task, job=job_stamp)


@pytest.fixture(scope="session")
def test_response_ok() -> TaskResponse[TaskTest]:
    task = TaskTest()
    job_stamp = JobStamp(
        status=JobStatus.completed, message="Job is completed"
    )
    return TaskResponse(task=task, job=job_stamp)


@pytest.fixture(scope="session")
def test_response_error() -> TaskResponse[TaskTest]:
    task = TaskTest()
    job_stamp = JobStamp(status=JobStatus.error, message="Error!")
    return TaskResponse(task=task, job=job_stamp)
