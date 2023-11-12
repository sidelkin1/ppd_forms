import shutil
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.dependencies.job.depot import JobDepot, JobDepotDep
from app.api.dependencies.user import UserDirDep, UserIdDep
from app.core.utils.job_manager import JobManager

router = APIRouter()


async def enqueue_job(
    websocket: WebSocket,
    job_depot: JobDepot,
    user_id: str,
    data: dict[str, Any],
) -> None:
    async with JobManager(websocket, job_depot, user_id, data) as manager:
        await manager.enqueue_job()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    job_depot: JobDepotDep,
    user_id: UserIdDep,
    directory: UserDirDep,
):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            job_depot.add_task(
                enqueue_job, websocket, job_depot, user_id, data
            )
    except WebSocketDisconnect:
        shutil.rmtree(directory, ignore_errors=True)
