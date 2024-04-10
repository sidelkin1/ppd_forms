import pytest

from app.core.models.dto import (
    TaskDatabase,
    TaskExcel,
    TaskInjLoss,
    TaskMatrix,
    TaskReport,
)
from app.core.models.enums import (
    ExcelTableName,
    LoadMode,
    LossMode,
    OfmTableName,
    ReportName,
)
from app.core.models.schemas import DateRange, MatrixEffect


@pytest.fixture(scope="session")
def date_range() -> DateRange:
    return DateRange(
        date_from="2020-01-01",
        date_to="2020-12-31",
    )


@pytest.fixture(scope="session")
def matrix_effect() -> MatrixEffect:
    return MatrixEffect(
        date_from="2020-01-01",
        date_to="2020-12-31",
        base_period=1,
        pred_period=12,
        excludes=[],
        on_date="2020-12-31",
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
def task_inj_loss(date_range: DateRange) -> TaskInjLoss:
    return TaskInjLoss(
        name=ReportName.inj_loss,
        mode=LossMode.first_rate,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )


@pytest.fixture(scope="session")
def task_matrix(matrix_effect: MatrixEffect) -> TaskMatrix:
    return TaskMatrix(
        name=ReportName.matrix,
        date_from=matrix_effect.date_from,
        date_to=matrix_effect.date_to,
        base_period=matrix_effect.base_period,
        pred_period=matrix_effect.pred_period,
        excludes=matrix_effect.excludes,
        on_date=matrix_effect.on_date,
    )
