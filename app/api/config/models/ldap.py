from typing import Any, cast

from pydantic import AnyUrl, Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LdapSettings(BaseSettings):
    host: str | None = Field(default=None, validation_alias="ldap_host")
    port: int | None = Field(default=None, validation_alias="ldap_port")
    url: AnyUrl = Field(default=None, validation_alias="ldap_url")
    timeout_s: int = Field(default=30, validation_alias="ldap_connect_timeout")

    @field_validator("url", mode="before")
    @classmethod
    def assemble_ldap_connection(cls, v: Any, info: ValidationInfo) -> Any:
        return v or AnyUrl.build(
            scheme="ldap",
            host=cast(str, info.data.get("host")),
            port=info.data.get("port"),
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
