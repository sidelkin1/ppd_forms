from pathlib import Path
from typing import Any

from arq.connections import RedisSettings
from pydantic import (
    DirectoryPath,
    FieldValidationInfo,
    FilePath,
    PostgresDsn,
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

    app_title: str = "Стандартные формы для ППД"
    app_description: str = "Приложение для создания типовых отчетов ППД"

    util_table_schema: str = "utils"

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
    def assemble_db_connection(cls, v: Any, info: FieldValidationInfo) -> Any:
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
    def assemble_redis_settings(cls, v: Any, info: FieldValidationInfo) -> Any:
        return v or RedisSettings(
            host=info.data["redis_host"], port=info.data["redis_port"]
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
