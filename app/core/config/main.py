from functools import lru_cache

from app.common.config.main import get_paths
from app.common.parsers import read_config
from app.core.config.models.app import AppSettings
from app.core.config.models.mmb import MmbSettings


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()  # type: ignore[call-arg]


@lru_cache
def get_mmb_settings() -> MmbSettings:
    paths = get_paths()
    mmb_config = read_config(paths.mmb_config)
    return MmbSettings(
        params=mmb_config["parameters"], press_tol=mmb_config["press_tol"]
    )
