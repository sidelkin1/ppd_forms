from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    title: str = Field(
        default="Стандартные формы для ППД", validation_alias="app_title"
    )
    description: str = Field(
        default="Приложение для создания типовых отчетов ППД",
        validation_alias="app_description",
    )
    delimiter: str = ","
    max_workers: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
