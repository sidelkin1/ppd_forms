import asyncio
import logging
from datetime import timedelta
from typing import Any

import structlog
from arq import ArqRedis
from arq.constants import abort_jobs_ss
from arq.jobs import Job, JobResult, ResultNotFound
from arq.jobs import JobStatus as ArqJobStatus
from redis.exceptions import RedisError

from app.core.models.dto import BaseResponse, JobResponse
from app.core.models.enums import JobStatus
from app.core.models.enums.task_id import TaskId
from app.infrastructure.redis.dao.job import ScheduledJobsDAO

logger = logging.getLogger(__name__)


class ArqDAO:
    def __init__(
        self, redis: ArqRedis, expires: timedelta, abort_timeout: float
    ):
        self.redis = redis
        self.abort_timeout = abort_timeout
        self.schedule = ScheduledJobsDAO(redis, expires=expires)

    async def enqueue_task(
        self, response: BaseResponse, username: str
    ) -> None:
        ctx = structlog.contextvars.get_contextvars()
        await self.redis.enqueue_job(
            "perform_work", response, ctx, _job_id=response.job.job_id
        )
        await self.schedule.add_job(username, response)

    async def response(self, job_id: str, username: str) -> JobResponse:
        if not (response := await self.schedule.get_job(username, job_id)):
            return JobResponse.not_found(job_id)
        job = Job(job_id=job_id, redis=self.redis)
        status = JobStatus.from_arq(await job.status())
        info = await job.info()
        if isinstance(info, JobResult):
            if info.success:
                response.result = info.result
                response.job.status = JobStatus.completed
            elif isinstance(info.result, asyncio.CancelledError):
                response.job.status = JobStatus.cancelled
                response.job.message = "Job is cancelled"
            else:
                response.job.status = JobStatus.error
                response.job.message = str(info.result)
        else:
            response.job.status = status
        return response

    async def cancel_job(self, job_id: str, username: str) -> JobResponse:
        """Прервать задачу пользователя и вернуть её состояние.

        Неизвестная или чужая задача — ``JobResponse.not_found``, как в
        ``response()``; завершившаяся сама (успехом, ошибкой или отменой) либо
        пропавшая из arq — её текущее состояние без обращения к ``abort()``.
        Если задача ещё в очереди/работе, ставится маркер отмены; подтверждения
        воркером ждём не дольше ``abort_timeout``, после чего возвращается
        ``in_progress`` (маркер остаётся и сработает, когда воркер возьмёт
        задачу). Код ответа выбирает api-слой.

        Ошибки Redis пробрасываются наверх.

        Повторный вызов для уже отменённой задачи возвращает ``cancelled`` —
        отмена идемпотентна.

        Отмена не прерывает уже запущенный процесс в ``ProcessPoolExecutor``:
        вычисление доработает до конца, частичные файлы подчистит
        ``cron_clean_files``.
        """
        if not await self.schedule.get_job(username, job_id):
            return JobResponse.not_found(job_id)
        job = Job(job_id=job_id, redis=self.redis)
        status = await job.status()
        if status in (ArqJobStatus.complete, ArqJobStatus.not_found):
            # есть результат или исполнение потеряно — нечего отменять
            return await self.response(job_id, username)
        try:
            cancelled = await job.abort(timeout=self.abort_timeout)
        except TimeoutError:
            # маркер уже поставлен, воркер не подтвердил за abort_timeout
            return await self.response(job_id, username)
        except RedisError:
            raise
        except Exception as error:
            # задача успела упасть: Job.abort пере-бросает её исключение
            logger.warning("Job %s was not cancelled", job_id, exc_info=error)
            cancelled = False
        if not cancelled:
            # завершилась, пока ждали, либо потеряна — снять свой маркер
            await self.redis.zrem(abort_jobs_ss, job_id)
        return await self.response(job_id, username)

    async def result(self, job_id: str, username: str) -> Any:
        if not await self.schedule.get_job(username, job_id):
            raise ResultNotFound(f"Задача {job_id} не найдена!")
        job = Job(job_id=job_id, redis=self.redis)
        return await job.result()

    async def get_scheduled_tasks(
        self, username: str, task_id: TaskId | None = None
    ) -> list[JobResponse]:
        responses = await self.schedule.get_jobs(username)
        if task_id:
            return [
                response
                for response in responses
                if response.task.get("task_id") == task_id
            ]
        return responses
