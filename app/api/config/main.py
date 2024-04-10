from functools import lru_cache

from app.api.config.models.api import ApiSettings
from app.api.config.models.auth import AuthSettings


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()  # type: ignore[call-arg]


@lru_cache
def get_api_settings() -> ApiSettings:
    return ApiSettings()  # type: ignore[call-arg]
