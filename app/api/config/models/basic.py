from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BasicAuthSettings(BaseSettings):
    username: str | None = Field(
        default=None, validation_alias="app_default_username"
    )
    password: str | None = Field(
        default=None, validation_alias="app_default_password"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
