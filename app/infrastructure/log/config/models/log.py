from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogSettings(BaseSettings):
    render_json_logs: bool = False
    log_path: Path | None = None
    log_level: str = "DEBUG"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
