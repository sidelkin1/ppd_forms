from functools import lru_cache

from app.infrastructure.files.config.models.csv import CsvSettings
from app.infrastructure.files.config.models.paths import Paths


@lru_cache
def get_csv_settings() -> CsvSettings:
    return CsvSettings()  # type: ignore[call-arg]


@lru_cache
def get_paths() -> Paths:
    return Paths()  # type: ignore[call-arg]
