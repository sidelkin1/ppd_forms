from functools import lru_cache

from app.infrastructure.files.config.models.csv import CsvSettings


@lru_cache
def get_csv_settings() -> CsvSettings:
    return CsvSettings()  # type: ignore[call-arg]
