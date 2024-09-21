from pathlib import Path

import pytest
from fastapi_pagination.utils import disable_installed_extensions_check  # noqa

from app.api.config.models.auth import AuthSettings
from app.api.config.models.basic import BasicAuthSettings
from app.common.config.models.paths import Paths
from app.core.config.models.app import AppSettings

disable_installed_extensions_check()


@pytest.fixture(scope="session")
def auth_config() -> AuthSettings:
    return AuthSettings(
        secret_key="secret_key",
        basic=BasicAuthSettings(  # type: ignore[call-arg]
            app_default_username="test_admin",
            app_default_password="test_password",
        ),
    )


@pytest.fixture(scope="session")
def app_config() -> AppSettings:
    return AppSettings()


@pytest.fixture(scope="session")
def paths(tmp_path_factory) -> Paths:
    base_dir = Path(__file__).resolve().parent.parent
    return Paths(
        base_dir=base_dir,
        data_dir=base_dir / "tests" / "fixtures" / "resources" / "data",
        file_dir=tmp_path_factory.mktemp("files"),
    )


@pytest.fixture(scope="session")
def result_dir(paths: Paths) -> Path:
    return paths.base_dir / "tests" / "fixtures" / "resources" / "results"
