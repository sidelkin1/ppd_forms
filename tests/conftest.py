from pathlib import Path

import pytest
from fastapi_pagination.utils import disable_installed_extensions_check

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
        site_dir=tmp_path_factory.mktemp("help"),
    )


@pytest.fixture(scope="session")
def result_dir(paths: Paths) -> Path:
    return paths.base_dir / "tests" / "fixtures" / "resources" / "results"


@pytest.fixture(scope="session")
def templates_dir(paths: Paths) -> Path:
    return paths.base_dir / "tests" / "fixtures" / "resources" / "templates"


@pytest.fixture(scope="session")
def well_test_template(paths: Paths) -> Path:
    """Шаблон отчёта из рабочего каталога data.

    Каталог data не хранится в репозитории, поэтому без него тесты,
    которым нужен шаблон, пропускаются.
    """
    template = paths.base_dir / "data" / "well_test_template.xlsx"
    if not template.is_file():
        pytest.skip(f"нет шаблона {template}")
    return template


@pytest.fixture(scope="session")
def well_test_arrow(paths: Paths) -> Path:
    """Указатель скважины для карты изобар из рабочего каталога data."""
    arrow = paths.base_dir / "data" / "well_test_arrow.png"
    if not arrow.is_file():
        pytest.skip(f"нет изображения {arrow}")
    return arrow
