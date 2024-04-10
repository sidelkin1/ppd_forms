from functools import lru_cache

from app.infrastructure.redis.config.models.redis import RedisSettings


@lru_cache
def get_redis_settings() -> RedisSettings:
    return RedisSettings()  # type: ignore[call-arg]
