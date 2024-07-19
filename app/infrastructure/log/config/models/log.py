from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogSettings(BaseSettings):
    render_json_logs: bool = False
    log_path: Path | None = None
    log_level: str = "DEBUG"
    log_backup_count: int = 5
    log_max_bytes: int = 1000000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
