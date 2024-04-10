from typing import Annotated

from pydantic import Field, UrlConstraints
from pydantic_core import Url
from pydantic_settings import BaseSettings, SettingsConfigDict

OracleDsn = Annotated[
    Url,
    UrlConstraints(
        allowed_schemes=[
            "oracle+oracledb",
            "oracle+cx_oracle",
        ]
    ),
]


class OracleSettings(BaseSettings):
    url: OracleDsn = Field(validation_alias="ofm_database_url")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
