from enum import Enum
from typing import Self

from arq.jobs import JobStatus as ArqJobStatus

_arq_mapper = {
    ArqJobStatus.deferred: "in_progress",
    ArqJobStatus.queued: "in_progress",
    ArqJobStatus.in_progress: "in_progress",
    ArqJobStatus.not_found: "not_found",
    ArqJobStatus.complete: "completed",
}


class JobStatus(str, Enum):
    created = "created"
    completed = "completed"
    in_progress = "in_progress"
    data_error = "data_error"
    execution_error = "execution_error"
    not_found = "not_found"

    @classmethod
    def from_arq(cls, status: ArqJobStatus) -> Self:
        return cls[_arq_mapper[status]]
