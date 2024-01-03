import asyncio

import pytest
from arq.jobs import Job
from fastapi.testclient import TestClient

from app.core.models.enums import JobStatus
from app.core.models.schemas import TaskResponse


def test_job_ok(
    test_client: TestClient, job_ok: Job, test_response_ok: TaskResponse
):
    with test_client.websocket_connect(
        f"jobs/{job_ok.job_id}/ws"
    ) as websocket:
        data = websocket.receive_json()
        assert data == test_response_ok.model_dump(exclude_none=True)


def test_job_error(
    test_client: TestClient, job_error: Job, test_response_error: TaskResponse
):
    with test_client.websocket_connect(
        f"jobs/{job_error.job_id}/ws"
    ) as websocket:
        data = websocket.receive_json()
        assert data == test_response_error.model_dump(exclude_none=True)


@pytest.mark.asyncio(scope="session")
async def test_job_abort(test_client: TestClient, job_abort: Job):
    with test_client.websocket_connect(f"jobs/{job_abort.job_id}/ws"):
        await asyncio.sleep(0.1)
    with pytest.raises(asyncio.CancelledError):
        await job_abort.result()


def test_job_is_not_found(test_client: TestClient):
    job_id = "unknown_job_id"
    with test_client.websocket_connect(f"jobs/{job_id}/ws") as websocket:
        data = websocket.receive_json()
        assert data == {
            "job": {
                "job_id": job_id,
                "message": "Job is not found",
                "status": JobStatus.not_found.value,
            }
        }
