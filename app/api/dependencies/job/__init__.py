from app.api.dependencies.job.current_job import CurrentJobDep  # noqa
from app.api.dependencies.job.current_job import (
    current_job_provider,
    get_job_stamp,
)
from app.api.dependencies.job.job_depot import JobDepotDep  # noqa
from app.api.dependencies.job.job_depot import (
    get_job_depot,
    job_depot_provider,
)
from app.api.dependencies.job.new_job import NewJobDep  # noqa
from app.api.dependencies.job.new_job import create_job_stamp, new_job_provider
