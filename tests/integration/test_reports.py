from collections.abc import Awaitable, Callable
from datetime import date
from pathlib import Path

import pytest
from csv_diff import compare, load_csv

from app.core.config.settings import Settings
from app.core.services.matrix_report import matrix_report
from app.core.services.oil_loss_report import oil_loss_report
from app.core.services.opp_per_year_report import opp_per_year_report
from app.core.services.profile_report import profile_report
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.dao.sql.reporters import LocalBaseDAO
from app.infrastructure.holder import HolderDAO


@pytest.mark.parametrize(
    "dao,service,expected_report",
    [
        (
            "well_profile_reporter",
            profile_report,
            "profile_report.csv",
        ),
        (
            "first_rate_loss_reporter",
            oil_loss_report,
            "first_rate_oil_loss.csv",
        ),
        (
            "max_rate_loss_reporter",
            oil_loss_report,
            "max_rate_oil_loss.csv",
        ),
        (
            "opp_per_year_reporter",
            opp_per_year_report,
            "opp_per_year_report.csv",
        ),
        (
            "matrix_reporter",
            matrix_report,
            "matrix_report.csv",
        ),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_reports(
    pool_holder: HolderDAO,
    process_pool: ProcessPoolManager,
    tmp_path: Path,
    settings: Settings,
    dao: str,
    service: Callable[..., Awaitable],
    expected_report: str,
    result_dir: Path,
):
    path = tmp_path / "results.csv"
    date_from = date(2000, 1, 1)
    date_to = date(2001, 1, 1)
    dao_: LocalBaseDAO = getattr(pool_holder, dao)
    if dao == "matrix_reporter":
        await service(
            path,
            date_from,
            date_to,
            1,
            12,
            [],
            date_to,
            dao_,
            process_pool,
            settings,
        )
    else:
        await service(path, date_from, date_to, dao_, process_pool, settings)
    diff = compare(
        load_csv(open(result_dir / expected_report)), load_csv(open(path))
    )
    for value in diff.values():
        assert not value
