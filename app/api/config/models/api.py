from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    host: str = Field(default="127.0.0.1", validation_alias="api_host")
    port: int = Field(default=8000, validation_alias="api_port")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
