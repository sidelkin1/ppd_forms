from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

from arq.connections import RedisSettings
from pydantic import (
    AnyUrl,
    DirectoryPath,
    FilePath,
    PostgresDsn,
    ValidationInfo,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.config.dsn import OracleDsn


class Settings(BaseSettings):
    base_dir: DirectoryPath = (
        Path(__file__).resolve().parent.parent.parent.parent
    )
    data_dir: DirectoryPath = base_dir / "data"
    file_dir: DirectoryPath = base_dir / "files"

    field_replace_path: FilePath = data_dir / "field_replace.csv"
    reservoir_replace_path: FilePath = data_dir / "reservoir_replace.csv"
    layer_replace_path: FilePath = data_dir / "layer_replace.csv"
    monthly_report_path: FilePath = data_dir / "monthly_report.csv"
    well_profile_path: FilePath = data_dir / "well_profile.csv"
    inj_well_database_path: FilePath | None = None
    neighborhood_path: FilePath | None = None
    new_strategy_inj_path: FilePath | None = None
    new_strategy_oil_path: FilePath | None = None

    app_title: str = "Стандартные формы для ППД"
    app_description: str = "Приложение для создания типовых отчетов ППД"

    delimiter: str = ","

    max_workers: int = 4

    csv_encoding: str = "cp1251"
    csv_delimiter: str = ";"

    ofm_database_url: OracleDsn

    db_host: str
    db_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    local_database_url: PostgresDsn = None

    @field_validator("local_database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Any, info: ValidationInfo) -> Any:
        return v or PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=info.data.get("postgres_user"),
            password=info.data.get("postgres_password"),
            host=info.data.get("db_host"),
            port=info.data.get("db_port"),
            path=info.data.get("postgres_db"),
        )

    redis_host: str
    redis_port: int
    redis_settings: RedisSettings = None

    @field_validator("redis_settings", mode="before")
    @classmethod
    def assemble_redis_settings(cls, v: Any, info: ValidationInfo) -> Any:
        return v or RedisSettings(
            host=info.data.get("redis_host"), port=info.data.get("redis_port")
        )

    ldap_host: str | None = None
    ldap_port: int | None = None
    ldap_url: AnyUrl = None

    @field_validator("ldap_url", mode="before")
    @classmethod
    def assemble_ldap_connection(cls, v: Any, info: ValidationInfo) -> Any:
        return v or AnyUrl.build(
            scheme="ldap",
            host=info.data.get("ldap_host"),
            port=info.data.get("ldap_port"),
        )

    app_default_username: str | None = None
    app_default_password: str | None = None

    token_expire_time: timedelta = timedelta(seconds=60)
    secret_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
