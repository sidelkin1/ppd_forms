from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def base_dir() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def data_dir(base_dir: Path) -> Path:
    return base_dir / "tests" / "fixtures" / "resources" / "data"


@pytest.fixture(scope="session")
def file_dir(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("files")


@pytest.fixture(scope="session")
def result_dir(base_dir: Path) -> Path:
    return base_dir / "tests" / "fixtures" / "resources" / "results"


@pytest.fixture(scope="session")
def secret_key() -> int:
    return 42
