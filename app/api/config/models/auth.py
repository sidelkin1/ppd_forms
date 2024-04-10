from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.api.config.models.basic import BasicAuthSettings
from app.api.config.models.ldap import LdapSettings


class AuthSettings(BaseSettings):
    basic: BasicAuthSettings = BasicAuthSettings()
    ldap: LdapSettings = LdapSettings()

    token_expire_time: timedelta = timedelta(days=7)
    secret_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
