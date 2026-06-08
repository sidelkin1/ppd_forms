from datetime import date

import pytest

from app.core.models.dto import (
    TaskCompensation,
    TaskDatabase,
    TaskExcel,
    TaskFNV,
    TaskInjLoss,
    TaskMatbal,
    TaskMatrix,
    TaskMmb,
    TaskOwcResp,
    TaskProlong,
    TaskReport,
    TaskWellTest,
    UneftFieldDB,
    UneftReservoirDB,
)
from app.core.models.enums import (
    ExcelTableName,
    Interpolation,
    LoadMode,
    LossMode,
    OfmTableName,
    ReportName,
    WellTest,
)
from app.core.models.schemas import (
    DateRange,
    FnvParams,
    InjLoss,
    MatbalParams,
    MatrixEffect,
    MmbParams,
    OnDate,
    OwcRespParams,
    ProlongParams,
    WellTestParams,
)

FIELD = UneftFieldDB(id=1, name="F1")
RESERVOIR = UneftReservoirDB(id=1, name="R1")


@pytest.fixture
def date_range() -> DateRange:
    return DateRange(
        date_from="2020-01-01",
        date_to="2020-12-31",
    )


@pytest.fixture
def inj_loss() -> InjLoss:
    return InjLoss(
        date_from="2020-01-01",
        date_to="2020-12-31",
        neighbs_from_ns_ppd=True,
    )


@pytest.fixture
def matrix_effect() -> MatrixEffect:
    return MatrixEffect(
        date_from="2020-01-01",
        date_to="2020-12-31",
        base_period=1,
        pred_period=12,
        excludes=[],
        on_date="2020-12-31",
    )


@pytest.fixture
def task_database(date_range: DateRange) -> TaskDatabase:
    return TaskDatabase(
        table=OfmTableName.profile,
        mode=LoadMode.refresh,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )


@pytest.fixture
def task_excel() -> TaskExcel:
    return TaskExcel(
        table=ExcelTableName.inj_db,
        mode=LoadMode.refresh,
        file="test.xlsx",
    )


@pytest.fixture
def task_report(date_range: DateRange) -> TaskReport:
    return TaskReport(
        name=ReportName.opp_per_year,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )


@pytest.fixture
def task_inj_loss(date_range: DateRange) -> TaskInjLoss:
    return TaskInjLoss(
        name=ReportName.inj_loss,
        mode=LossMode.first_rate,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
        neighbs_from_ns_ppd=True,
    )


@pytest.fixture
def task_matrix(matrix_effect: MatrixEffect) -> TaskMatrix:
    return TaskMatrix(
        name=ReportName.matrix,
        date_from=matrix_effect.date_from,
        date_to=matrix_effect.date_to,
        base_period=matrix_effect.base_period,
        pred_period=matrix_effect.pred_period,
        excludes=matrix_effect.excludes,
        on_date=matrix_effect.on_date,
        wells=None,
    )


@pytest.fixture
def fnv() -> FnvParams:
    return FnvParams(
        fields=[FIELD],
        min_radius=0,
        alternative=False,
        max_fields=1,
    )


@pytest.fixture
def task_fnv() -> TaskFNV:
    return TaskFNV(
        name=ReportName.fnv,
        fields=[FIELD],
        min_radius=0,
        alternative=False,
        max_fields=1,
    )


@pytest.fixture
def matbal() -> MatbalParams:
    return MatbalParams(
        field=FIELD,
        reservoirs=[RESERVOIR],
        wells=None,
        measurements=None,
        alternative=False,
    )


@pytest.fixture
def task_matbal() -> TaskMatbal:
    return TaskMatbal(
        name=ReportName.matbal,
        field=FIELD,
        reservoirs=[RESERVOIR],
        wells=None,
        measurements=None,
        alternative=False,
    )


@pytest.fixture
def prolong() -> ProlongParams:
    return ProlongParams(
        expected="expected.xlsx",
        actual="actual.xlsx",
        interpolations=[Interpolation.akima],
    )


@pytest.fixture
def task_prolong() -> TaskProlong:
    return TaskProlong(
        name=ReportName.prolong,
        expected="expected.xlsx",
        actual="actual.xlsx",
        interpolations=[Interpolation.akima],
    )


@pytest.fixture
def mmb() -> MmbParams:
    return MmbParams(file="tank.xlsx", alternative=False)


@pytest.fixture
def task_mmb() -> TaskMmb:
    return TaskMmb(name=ReportName.mmb, file="tank.xlsx", alternative=False)


@pytest.fixture
def on_date() -> OnDate:
    return OnDate(on_date=date(2020, 12, 31))


@pytest.fixture
def task_compensation() -> TaskCompensation:
    return TaskCompensation(
        name=ReportName.compensation,
        on_date=date(2020, 12, 31),
    )


@pytest.fixture
def well_test() -> WellTestParams:
    return WellTestParams(
        file="well_test.xlsx",
        gtm_period=6,
        gdis_period=3,
        radius=300,
    )


@pytest.fixture
def task_well_test() -> TaskWellTest:
    return TaskWellTest(
        name=ReportName.well_test,
        file="well_test.xlsx",
        gtm_period=6,
        gdis_period=3,
        radius=300,
    )


@pytest.fixture
def owc_resp_static() -> OwcRespParams:
    return OwcRespParams(
        field=FIELD,
        reservoir=RESERVOIR,
        well="  w1  ",
        pressure=100,
        depth=75,
        well_test=WellTest.static_level,
        on_date=date(2025, 10, 20),
    )


@pytest.fixture
def task_owc_resp_static() -> TaskOwcResp:
    return TaskOwcResp(
        name=ReportName.owc_resp,
        field=FIELD,
        reservoir=RESERVOIR,
        well="W1",
        pressure=100,
        depth=75,
        well_test=WellTest.static_level,
        on_date=date(2025, 10, 20),
    )


@pytest.fixture
def owc_resp_pressure() -> OwcRespParams:
    return OwcRespParams(
        field=FIELD,
        reservoir=RESERVOIR,
        well="  w2  ",
        pressure=100,
        depth=75,
        well_test=WellTest.pressure,
        on_date=date(2025, 10, 20),
    )


@pytest.fixture
def task_owc_resp_pressure() -> TaskOwcResp:
    return TaskOwcResp(
        name=ReportName.owc_resp,
        field=FIELD,
        reservoir=RESERVOIR,
        well="W2",
        pressure=100,
        depth=75,
        well_test=WellTest.pressure,
        on_date=date(2025, 10, 20),
    )
