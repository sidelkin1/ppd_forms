from typing import Any

from pydantic import Field, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    host: str | None = Field(default=None, validation_alias="db_host")
    port: int | None = Field(default=None, validation_alias="db_port")
    user: str | None = Field(default=None, validation_alias="postgres_user")
    password: str | None = Field(
        default=None, validation_alias="postgres_password"
    )
    db: str | None = Field(default=None, validation_alias="postgres_db")
    url: PostgresDsn = Field(
        default=None, validation_alias="local_database_url"
    )  # type: ignore[assignment]

    @field_validator("url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Any, info: ValidationInfo) -> Any:
        return v or PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=info.data.get("user"),
            password=info.data.get("password"),
            host=info.data.get("host"),
            port=info.data.get("port"),
            path=info.data.get("db"),
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
