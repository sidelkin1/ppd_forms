from functools import lru_cache

from app.infrastructure.log.config.models.log import LogSettings


@lru_cache
def get_log_settings() -> LogSettings:
    return LogSettings()  # type: ignore[call-arg]
