from functools import lru_cache

from app.common.config.models.paths import Paths


@lru_cache
def get_paths() -> Paths:
    return Paths()  # type: ignore[call-arg]
