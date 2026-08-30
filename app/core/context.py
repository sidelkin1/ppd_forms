"""Типизированный контекст worker'а (заменяет dict[str, Any])."""

from dataclasses import dataclass

from app.common.config.models.paths import Paths
from app.core.config.models.app import AppSettings
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.files.config.models.csv import CsvSettings
from app.infrastructure.reporters import Reporters
from app.infrastructure.sessions import Sessions


@dataclass(frozen=True)
class WorkerContext:
    settings: AppSettings
    csv: CsvSettings
    paths: Paths
    sessions: Sessions
    reporters: Reporters
    process_pool: ProcessPoolManager
