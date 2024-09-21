from datetime import timedelta
from typing import Annotated

from pydantic import Field
from pydantic.functional_validators import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    title: str = Field(
        default="Стандартные формы для ППД", validation_alias="app_title"
    )
    description: str = Field(
        default="Приложение для создания типовых отчетов ППД",
        validation_alias="app_description",
    )
    delimiter: str = Field(default=",", validation_alias="app_delimiter")
    max_workers: int = Field(default=4, validation_alias="app_max_workers")
    root_path: str = Field(default="", validation_alias="app_root_path")
    keep_result: Annotated[timedelta, BeforeValidator(int)] = Field(
        default=86400, validation_alias="app_keep_result"
    )
    page_size: int = Field(default=5, validation_alias="app_page_size")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
