from functools import lru_cache

from app.infrastructure.db.config.models.local import PostgresSettings
from app.infrastructure.db.config.models.ofm import OracleSettings


@lru_cache
def get_postgres_settings() -> PostgresSettings:
    return PostgresSettings()  # type: ignore[call-arg]


@lru_cache
def get_oracle_settings() -> OracleSettings:
    return OracleSettings()  # type: ignore[call-arg]
