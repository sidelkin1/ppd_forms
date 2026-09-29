from datetime import datetime
from typing import Any, Self

from app.core.models.dto.jobs.job_stamp import JobStamp
from app.core.models.dto.responses.base import BaseResponse
from app.core.models.enums import JobStatus


class JobResponse(BaseResponse[dict[str, Any]]):
    @classmethod
    def not_found(cls, job_id: str) -> Self:
        return cls(
            task={},
            job=JobStamp(
                job_id=job_id,
                status=JobStatus.not_found,
                message="Job is not found",
                created_at=datetime.min,
            ),
        )
