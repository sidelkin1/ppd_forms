import logging
from collections.abc import Awaitable, Callable
from datetime import date
from filecmp import cmpfiles
from pathlib import Path

import pandas as pd
import pytest
import structlog
from openpyxl import load_workbook

from app.common.config.models.paths import Paths
from app.core.models.dto import UneftFieldDB
from app.core.services.reports import (
    fnv_report,
    inj_loss_report,
    isobar_report,
    matrix_report,
    oil_loss_report,
    opp_per_year_report,
    owc_resp_report,
    profile_report,
)
from app.core.services.reports.isobar.columns import SHEET as ISOBAR_SHEET
from app.core.services.reports.isobar.preparation import prepare_dataframe
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.dao.sql.reporters import LocalBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import (
    isobar as isobar_querysets,
)
from app.infrastructure.holder import HolderDAO
from tests.fixtures.task_fixtures import (  # noqa
    task_owc_resp_pressure,
    task_owc_resp_static,
)


@pytest.mark.parametrize(
    "dao,service,expected_report,resulted_report",
    [
        (
            "well_profile_reporter",
            profile_report,
            "profile_report.xlsx",
            "profile.xlsx",
        ),
        (
            "first_rate_inj_loss_reporter",
            inj_loss_report,
            "first_rate_inj_loss_report.xlsx",
            "inj_loss.xlsx",
        ),
        (
            "max_rate_inj_loss_reporter",
            inj_loss_report,
            "max_rate_inj_loss_report.xlsx",
            "inj_loss.xlsx",
        ),
        (
            "first_rate_oil_loss_reporter",
            oil_loss_report,
            "first_rate_oil_loss_report.xlsx",
            "oil_loss.xlsx",
        ),
        (
            "max_rate_oil_loss_reporter",
            oil_loss_report,
            "max_rate_oil_loss_report.xlsx",
            "oil_loss.xlsx",
        ),
        (
            "opp_per_year_reporter",
            opp_per_year_report,
            "opp_per_year_report.xlsx",
            "opp_per_year.xlsx",
        ),
        (
            "matrix_reporter",
            matrix_report,
            "matrix_report.xlsx",
            "matrix.xlsx",
        ),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_reports(
    pool_holder: HolderDAO,
    process_pool: ProcessPoolManager,
    tmp_path: Path,
    dao: str,
    service: Callable[..., Awaitable],
    expected_report: str,
    resulted_report: str,
    result_dir: Path,
):
    date_from = date(2000, 1, 1)
    date_to = date(2001, 1, 1)
    dao_: LocalBaseDAO = getattr(pool_holder, dao)
    if dao == "matrix_reporter":
        await service(
            tmp_path,
            date_from,
            date_to,
            1,
            12,
            [],
            date_to,
            dao_,
            process_pool,
            ",",
        )
    elif dao in (
        "opp_per_year_reporter",
        "first_rate_oil_loss_reporter",
        "max_rate_oil_loss_reporter",
    ):
        await service(tmp_path, date_from, date_to, dao_, process_pool)
    elif dao in (
        "first_rate_inj_loss_reporter",
        "max_rate_inj_loss_reporter",
    ):
        await service(
            tmp_path, date_from, date_to, True, dao_, process_pool, ","
        )
    else:
        await service(tmp_path, date_from, date_to, dao_, process_pool, ",")
    df_expected = pd.read_excel(result_dir / expected_report)
    df_actual = pd.read_excel(tmp_path / resulted_report)
    pd.testing.assert_frame_equal(df_actual, df_expected, atol=1e-4)


@pytest.mark.asyncio(scope="session")
async def test_isobar_local_queries(pool_holder: HolderDAO):
    reporter = pool_holder.local_isobar_reporter

    succeeded = await reporter.read_one(
        key="succeeded",
        date_from=date(2019, 1, 1),
        date_to=date(2021, 1, 1),
    )
    assert len(succeeded) == 2

    first = await reporter.read_previous(
        [("F1", "W1", date(2020, 1, 10), "R1")]
    )
    assert len(first) == 1
    assert first["reservoir"].item() == "R1"
    assert first["well_type"].item() == "НЕФ"
    assert first["well_status"].item() == "РАБ"

    # тот же замер и дата, но другой объект — своя запись
    second = await reporter.read_previous(
        [("F1", "W1", date(2020, 1, 10), "R2")]
    )
    assert len(second) == 1
    assert second["well_type"].item() == "НАГ"
    assert second["well_status"].item() == "НАК"

    # объекта нет в замерах — M/N не заполнятся
    unknown = await reporter.read_previous(
        [("F1", "W1", date(2020, 1, 10), "R3")]
    )
    assert unknown.empty

    missed = await reporter.read_previous(
        [("F1", "W1", date(2020, 5, 1), "R1")]
    )
    assert missed.empty

    empty = await reporter.read_previous([])
    assert empty.empty
    assert list(empty.columns) == list(isobar_querysets.PREV_COLUMNS)


@pytest.mark.asyncio(scope="session")
async def test_fnv_report(
    pool_holder: HolderDAO,
    tmp_path: Path,
    result_dir: Path,
    caplog,
):
    caplog.set_level(logging.DEBUG)
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id="1234567890", user_id="test_user"
    )
    fnv_dir = result_dir / "fnv"
    field = UneftFieldDB(id=1, name="F1")
    min_radius = 0
    alternative = False
    await fnv_report(
        tmp_path,
        field,
        min_radius,
        alternative,
        pool_holder.fnv_reporter,
    )
    parts = ["/".join(file.parts[-2:]) for file in fnv_dir.glob("*/*.txt")]
    _, mismatch, errors = cmpfiles(tmp_path, fnv_dir, parts)
    assert not mismatch
    assert not errors


@pytest.mark.asyncio(scope="session")
@pytest.mark.parametrize(
    (
        "task_fixture,expected_plan,expected_bl,expected_bm,"
        "expected_bn,expected_bo,empty_depths"
    ),
    [
        (
            "task_owc_resp_static",
            "Pпл по Hст",
            75,
            100,
            None,
            None,
            False,
        ),
        (
            "task_owc_resp_pressure",
            "Pпл",
            None,
            None,
            75,
            100,
            False,
        ),
        (
            "task_owc_resp_pressure",
            "Pпл",
            None,
            None,
            75,
            100,
            True,
        ),
    ],
)
async def test_owc_resp_report(
    pool_holder: HolderDAO,
    process_pool: ProcessPoolManager,
    paths: Paths,
    tmp_path: Path,
    request,
    task_fixture: str,
    expected_plan: str,
    expected_bl: float | None,
    expected_bm: float | None,
    expected_bn: float | None,
    expected_bo: float | None,
    empty_depths: bool,
):
    task = request.getfixturevalue(task_fixture)
    path = tmp_path / "owc_resp"
    path.mkdir()
    data_dir = paths.base_dir / "data"
    calculator_template = data_dir / "owc_resp_template.xlsx"
    analytics_template = data_dir / "analytics_template.xlsx"
    pool_holder.kwargs["empty_depths"] = empty_depths
    await owc_resp_report(
        path,
        calculator_template,
        analytics_template,
        task.field,
        task.reservoir,
        task.well,
        task.pressure,
        task.depth,
        task.well_test,
        task.on_date,
        pool_holder.owc_resp_reporter,
        process_pool,
    )

    analytics = load_workbook(
        path / "analytics_template.xlsx", data_only=False
    )
    calc = load_workbook(path / "owc_resp_template.xlsx", data_only=False)

    analytics_ws = analytics["Лист1"]
    calc_ws = calc["Пересчет"]

    assert analytics_ws["AW5"].value == expected_plan
    assert analytics_ws["BE5"].value == "20.10.2025"
    assert analytics_ws["BF5"].value == "20.10.2025"
    assert analytics_ws["BL5"].value == expected_bl
    assert analytics_ws["BM5"].value == expected_bm
    assert analytics_ws["BN5"].value == expected_bn
    assert analytics_ws["BO5"].value == expected_bo
    if empty_depths:
        assert analytics_ws["BY5"].value is None
        assert analytics_ws["BZ5"].value is None
    else:
        assert analytics_ws["BY5"].value == pytest.approx(102.5)
        assert analytics_ws["BZ5"].value == pytest.approx(103.5)
    assert calc_ws["B15"].value == pytest.approx(1.0)


@pytest.mark.asyncio(scope="session")
async def test_isobar_report(
    tmp_path: Path,
    process_pool: ProcessPoolManager,
    templates_dir: Path,
    holder_factory: Callable[..., HolderDAO],
):
    template = templates_dir / "isobar_template.xlsx"
    holder = holder_factory(path=template)
    result = tmp_path / "result"
    result.mkdir()
    await isobar_report(
        result,
        template,
        date(2026, 7, 1),
        date(2026, 10, 1),
        date(2026, 9, 1),
        holder.isobar_reporter,
        process_pool,
    )

    assert Path(str(result) + ".zip").exists()
    book = result / "СВОДНЫЙ_ИЗОБАРЫ_01.10.2026.xlsx"
    assert book.exists()
    wb = load_workbook(book)
    ws = wb[ISOBAR_SHEET]
    assert ws.max_row == 5

    # W1: старые значения в J-N, квартальный замер обновил O-Q и AC-AE
    assert ws["C2"].value == "F1"
    assert ws["D2"].value == "R1"
    assert ws["E2"].value == "W1"
    assert ws["F2"].value == "неф"
    assert ws["G2"].value == "раб."
    assert ws["H2"].value == "=IF(O2>0,O2,AN2)"
    assert ws["AF2"].value == '=IF(AND(J2>0,O2>0),O2-J2,"-")'
    assert ws["I2"].value == pytest.approx(95.0)
    assert ws["J2"].value == pytest.approx(100.0)
    assert ws["K2"].value.date() == date(2026, 2, 1)
    assert ws["L2"].value == "КВД"
    assert ws["M2"].value == "НЕФ"
    assert ws["N2"].value == "РАБ"
    assert ws["O2"].value == pytest.approx(105.0)
    assert ws["P2"].value.date() == date(2026, 8, 1)
    assert ws["Q2"].value == "КВД"
    assert ws["AC2"].value == pytest.approx(90.0)
    assert ws["AD2"].value.date() == date(2026, 8, 1)
    assert ws["AE2"].value == "КВУ"
    assert ws["AH2"].value == pytest.approx(60.0)
    assert ws["R2"].value is None

    # W2: замер сделан на стволе W2B1, поэтому в строке W2 его нет
    assert ws["E3"].value == "W2"
    assert ws["H3"].value == "=IF(O3>0,O3,AN3)"
    assert ws["I3"].value is None
    assert ws["J3"].value is None
    assert ws["K3"].value is None
    assert ws["M3"].value is None
    assert ws["N3"].value is None
    assert ws["O3"].value is None
    assert ws["P3"].value is None
    assert ws["Q3"].value is None
    assert ws["AC3"].value is None
    assert ws["AD3"].value is None
    assert ws["AH3"].value == pytest.approx(70.0)

    # W2B1: квартальный замер привязался к стволу, работавшему на его дату
    assert ws["E4"].value == "W2B1"
    assert ws["G4"].value == "[стар. ствол]"
    assert ws["H4"].value == "=IF(O4>0,O4,AN4)"
    assert ws["AF4"].value == '=IF(AND(J4>0,O4>0),O4-J4,"-")'
    assert ws["I4"].value is None
    assert ws["J4"].value is None
    assert ws["O4"].value == pytest.approx(111.0)
    assert ws["P4"].value.date() == date(2026, 8, 1)
    assert ws["Q4"].value == "КВД"
    assert ws["AC4"].value == pytest.approx(80.0)
    assert ws["AD4"].value.date() == date(2026, 8, 1)
    assert ws["AE4"].value == "КВУ"
    assert ws["AH4"].value == pytest.approx(70.0)

    # W3: квартальных замеров нет — старые значения перенесены в O-Q;
    # AC-AE из сводной не переносятся (только новые квартальные замеры)
    assert ws["E5"].value == "W3"
    assert ws["J5"].value == pytest.approx(98.0)
    assert ws["K5"].value.date() == date(2026, 4, 1)
    assert ws["M5"].value == "НЕФ"
    assert ws["N5"].value == "РАБ"
    assert ws["O5"].value == pytest.approx(98.0)
    assert ws["P5"].value.date() == date(2026, 4, 1)
    assert ws["Q5"].value == "КВД"
    assert ws["AC5"].value is None
    assert ws["AD5"].value is None
    assert ws["AE5"].value is None
    assert ws["AH5"].value == pytest.approx(80.0)
    wb.close()

    state_misses = result / "СВОДНЫЙ_ИЗОБАРЫ_01.10.2026_нет_данных_гдис.csv"
    assert state_misses.exists()
    text = state_misses.read_text(encoding="utf-8-sig")
    header = text.splitlines()[0]
    assert "Вид исследования" in header
    assert "Рпл" in header
    assert "Хар-р работы" not in header
    assert "W4" in text
    assert "W5" in text
    assert "97.0" in text

    # строки сводной с Рпл, которым нет пары в фонде (W4, W5)
    lost_previous = (
        result / "СВОДНЫЙ_ИЗОБАРЫ_01.10.2026_нет_в_фонде_сводная.csv"
    )
    assert lost_previous.exists()
    text = lost_previous.read_text(encoding="utf-8-sig")
    assert "W4" in text
    assert "W5" in text
    assert "97.0" in text

    # текущие замеры из welltest все попали в фонд — файла нет
    lost_tests = result / "СВОДНЫЙ_ИЗОБАРЫ_01.10.2026_нет_в_фонде_welltest.csv"
    assert not lost_tests.exists()


@pytest.mark.asyncio(scope="session")
async def test_isobar_previous_reservoir_mapping(
    templates_dir: Path,
    holder_factory: Callable[..., HolderDAO],
):
    """D файла после reservoir_mapper совпадает с cid (в т.ч. «(Руд)»)."""
    template = templates_dir / "isobar_previous.xlsx"
    holder = holder_factory(path=template)
    previous = await holder.file_isobar_reporter.read_previous()
    assert previous["reservoir"].tolist() == ["Тур"]

    tests_columns = [
        "field",
        "well",
        "reservoir",
        "branch",
        "well_test",
        "end_date",
        "resp_owc",
        "curator",
    ]
    dfs = {
        "stock": pd.DataFrame(
            {
                "field": ["Заборское"],
                "well_name": ["206"],
                "parent": ["206"],
                "reservoir": ["турнейский(рудинский)"],
                "cid": ["Тур"],
                "type_": ["неф"],
                "status": ["раб."],
                "p_init": [150.0],
                "p_bubble": [60.0],
            }
        ),
        "succeeded": pd.DataFrame(columns=tests_columns),
        "failed": pd.DataFrame(columns=tests_columns),
        "perfs": pd.DataFrame(
            columns=[
                "field",
                "well",
                "reservoir",
                "branch",
                "comp_date",
                "close_date",
            ]
        ),
        "prev_values": previous,
        "prev_state": pd.DataFrame(
            columns=[
                "field",
                "well",
                "end_date",
                "reservoir",
                "well_type",
                "well_status",
            ]
        ),
    }
    df = prepare_dataframe(dfs)
    assert df.loc[0, "prev_date"] == date(2026, 6, 1)
    assert df.loc[0, "prev_resp"] == pytest.approx(150.0)
    assert df.loc[0, "prev_well_test"] == "КВД"
