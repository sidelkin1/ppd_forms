from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CsvSettings(BaseSettings):
    encoding: str = Field(default="cp1251", validation_alias="csv_encoding")
    delimiter: str = Field(default=";", validation_alias="csv_delimiter")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
