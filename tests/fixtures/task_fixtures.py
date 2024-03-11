import pytest

from app.core.models.dto import (
    TaskDatabase,
    TaskExcel,
    TaskOilLoss,
    TaskReport,
)
from app.core.models.enums import (
    ExcelTableName,
    LoadMode,
    LossMode,
    OfmTableName,
    ReportName,
)
from app.core.models.schemas import DateRange


@pytest.fixture(scope="session")
def date_range() -> DateRange:
    return DateRange(
        date_from="2020-01-01",
        date_to="2020-12-31",
    )


@pytest.fixture(scope="session")
def task_database(date_range: DateRange) -> TaskDatabase:
    return TaskDatabase(
        table=OfmTableName.profile,
        mode=LoadMode.refresh,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )


@pytest.fixture(scope="session")
def task_excel() -> TaskExcel:
    return TaskExcel(
        table=ExcelTableName.inj_db,
        mode=LoadMode.refresh,
        file="test.xlsx",
    )


@pytest.fixture(scope="session")
def task_report(date_range: DateRange) -> TaskReport:
    return TaskReport(
        name=ReportName.opp_per_year,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )


@pytest.fixture(scope="session")
def task_oil_loss(date_range: DateRange) -> TaskOilLoss:
    return TaskOilLoss(
        name=ReportName.oil_loss,
        mode=LossMode.first_rate,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )
