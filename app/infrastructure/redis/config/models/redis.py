from typing import Any, cast

from arq.connections import RedisSettings as ArqRedisSettings
from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    host: str | None = Field(default=None, validation_alias="redis_host")
    port: int | None = Field(default=None, validation_alias="redis_port")
    arq_settings: ArqRedisSettings = None  # type: ignore[assignment]

    @field_validator("arq_settings", mode="before")
    @classmethod
    def assemble_redis_settings(cls, v: Any, info: ValidationInfo) -> Any:
        return v or ArqRedisSettings(
            host=cast(str, info.data.get("host")),
            port=cast(int, info.data.get("port")),
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
