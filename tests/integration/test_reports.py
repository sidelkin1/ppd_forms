from datetime import date
from pathlib import Path
from typing import Callable

import pytest
from csv_diff import compare, load_csv

from app.core.config.settings import Settings
from app.core.services.oil_loss_report import oil_loss_report
from app.core.services.profile_report import profile_report
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.holder import HolderDAO


@pytest.mark.parametrize(
    "dao,service,expected_report",
    [
        ("well_profile_reporter", profile_report, "profile_report.csv"),
        (
            "first_rate_loss_reporter",
            oil_loss_report,
            "first_rate_oil_loss.csv",
        ),
        ("max_rate_loss_reporter", oil_loss_report, "max_rate_oil_loss.csv"),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_reports(
    pool_holder: HolderDAO,
    process_pool: ProcessPoolManager,
    tmp_path: Path,
    settings: Settings,
    dao: str,
    service: Callable[..., None],
    expected_report: str,
):
    base_dir = Path(__file__).resolve().parent.parent.parent
    result_dir = base_dir / "tests" / "fixtures" / "resources" / "results"
    path = tmp_path / "results.csv"
    date_from = date(2000, 1, 1)
    date_to = date(2001, 1, 1)
    await service(
        path,
        date_from,
        date_to,
        getattr(pool_holder, dao),
        process_pool,
        settings,
    )
    diff = compare(
        load_csv(open(result_dir / expected_report)), load_csv(open(path))
    )
    for value in diff.values():
        assert not value
