from datetime import date
from pathlib import Path

import pytest
from csv_diff import compare, load_csv
from sqlalchemy.orm import sessionmaker

from app.core.config.settings import Settings
from app.core.services.profile_report import profile_report
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.dao.sql.reporters import WellProfileReporter

base_dir = Path(__file__).resolve().parent.parent.parent
result_dir = base_dir / "tests" / "fixtures" / "resources" / "results"


@pytest.mark.asyncio(scope="session")
async def test_profile_report(
    pool: sessionmaker,
    process_pool: ProcessPoolManager,
    tmp_path: Path,
    settings: Settings,
):
    path = tmp_path / "results.csv"
    dao = WellProfileReporter(pool)
    date_from = date(2000, 1, 1)
    date_to = date(2001, 1, 1)
    await profile_report(path, date_from, date_to, dao, process_pool, settings)
    diff = compare(
        load_csv(open(result_dir / "profile_report.csv")), load_csv(open(path))
    )
    for value in diff.values():
        assert not value
