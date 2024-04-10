from functools import lru_cache

from app.core.config.models.app import AppSettings


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()  # type: ignore[call-arg]
