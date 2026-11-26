"""Ствол текущего и предыдущих ГДИС и заполнение Excel-отчёта."""

from datetime import date
from pathlib import Path
from typing import Any, cast

import openpyxl
import pandas as pd
import pytest
from openpyxl.worksheet.worksheet import Worksheet

from app.core.models.dto import WellTestResult
from app.core.services.reports.well_test import (
    _concat_tests,
    _process_data,
    _resolve_history_branches,
)
from app.infrastructure.db.dao.complex.reporters.well_test import (
    WellTestReporter,
)
from app.infrastructure.db.dao.sql.reporters.ofm_well_test import PERF_COLUMNS
from tests.mocks.reporters import (
    FileWellTestMock,
    LocalWellTestMock,
    OfmWellTestMock,
)

_HISTORY_COLUMNS = (
    "field",
    "well",
    "reservoir",
    "well_type",
    "well_test",
    "end_date",
    "resp_owc",
    "permeability",
    "skin_factor",
    "prod_index",
    "frac_length",
    "reliability",
    "layer",
)

_GTM_COLUMNS = (
    "field",
    "well",
    "reservoir",
    "well_type",
    "gtm_date",
    "gtm_name",
    "gtm_description",
)

_NEIGHB_COLUMNS = (
    "field",
    "well",
    "reservoir",
    "distance",
    "well_layer",
)


def _file_result(
    *,
    field: str = "Котовское",
    well: str = "303",
    reservoir: str = "Вз",
    end_date: date = date(2026, 8, 1),
) -> WellTestResult:
    """Результат чтения файла ГДИС — ещё без поля ``branch``."""
    return cast(
        WellTestResult,
        {
            "field": field,
            "reservoir": reservoir,
            "report_reservoir": "Визейский",
            "well": well,
            "well_type": "добывающая",
            "well_test": "КВД",
            "end_date": end_date,
            "permeability": 1.0,
            "skin_factor": 0.0,
            "resp_owc": 100.0,
            "prod_index": None,
            "frac_length": None,
            "reliability": "Хорошая",
            "isobars": None,
            "purpose": "Цель",
        },
    )


def _reporter(
    results: list[WellTestResult], ofm: OfmWellTestMock
) -> WellTestReporter:
    return WellTestReporter(
        history=LocalWellTestMock(pd.DataFrame()),
        results=FileWellTestMock(results),
        ofm=ofm,
    )


def _history_row(
    *,
    well: str = "303",
    layer: str = "Вз",
    reservoir: str = "Вз",
    end_date: date = date(2025, 6, 1),
) -> dict[str, Any]:
    return {
        "field": "Котовское",
        "well": well,
        "layer": layer,
        "reservoir": reservoir,
        "well_type": "добывающая",
        "well_test": "КВД",
        "end_date": end_date,
        "resp_owc": 100.0,
        "permeability": 1.0,
        "skin_factor": 0.0,
        "prod_index": None,
        "frac_length": None,
        "reliability": "Хорошая",
    }


def _history(*rows: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(list(rows), columns=list(_HISTORY_COLUMNS))


def _perf(
    *,
    branch: str = "303B1",
    comp_date: date = date(2020, 1, 1),
    close_date: date | None = None,
    well: str = "303",
    reservoir: str = "Вз",
) -> dict[str, Any]:
    return {
        "field": "Котовское",
        "well": well,
        "reservoir": reservoir,
        "branch": branch,
        "comp_date": comp_date,
        "close_date": close_date,
    }


def _perfs(*rows: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(list(rows), columns=list(PERF_COLUMNS))


def _current_result(branch: str = "303B2") -> WellTestResult:
    return cast(WellTestResult, {**_file_result(), "branch": branch})


def _gtm_row(
    *,
    gtm_date: date = date(2025, 12, 1),
    reservoir: str = "Вз",
) -> dict[str, Any]:
    return {
        "field": "Котовское",
        "well": "303",
        "reservoir": reservoir,
        "well_type": "добывающая",
        "gtm_date": gtm_date,
        "gtm_name": "ГРП",
        "gtm_description": "Гидроразрыв пласта",
    }


def _gtms(*rows: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(list(rows), columns=list(_GTM_COLUMNS))


def _empty_neighbs() -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        pd.DataFrame(columns=["field", "well", "reservoir"]),
        pd.DataFrame(columns=list(_NEIGHB_COLUMNS)),
    )


def _report_dfs(
    tests: pd.DataFrame,
    perfs: pd.DataFrame,
    gtms: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    neighb_tests, neighbs = _empty_neighbs()
    return {
        "tests": tests,
        "perfs": perfs,
        "gtms": gtms,
        "pvt": pd.DataFrame(
            {"reservoir": ["Вз"], "p_init": [150.0], "p_bubble": [100.0]}
        ),
        "neighb_tests": neighb_tests,
        "neighbs": neighbs,
    }


def _run_report(
    tmp_path: Path,
    dfs: dict[str, pd.DataFrame],
    results: list[WellTestResult],
    template: Path,
    arrow: Path,
) -> tuple[openpyxl.Workbook, pd.DataFrame]:
    history = dfs["tests"]
    _process_data(results, dfs, tmp_path, template, arrow)
    wb = openpyxl.load_workbook(tmp_path / template.name)
    return wb, history


def _assert_column_m_blank(ws: Worksheet, rows: range) -> None:
    """В строках ГТМ столбец M остаётся без значения.

    Оформление при этом обводится и заливается как у остальной строки
    ГТМ, поэтому проверяется только отсутствие значения: текст в M
    попал бы в ряд давления и дал бы точку в нуле.
    """
    for row in rows:
        assert ws[f"M{row}"].value is None


@pytest.mark.asyncio
async def test_get_results_fills_branch_per_object_and_date() -> None:
    results = [
        _file_result(reservoir="Вз", end_date=date(2026, 8, 1)),
        _file_result(reservoir="Тур", end_date=date(2026, 8, 1)),
        _file_result(reservoir="Вз", end_date=date(2026, 9, 1)),
    ]
    ofm = OfmWellTestMock(
        found={
            ("303", "Вз", date(2026, 8, 1)): "303B2",
            ("303", "Тур", date(2026, 8, 1)): "303B1",
            ("303", "Вз", date(2026, 9, 1)): "303B3",
        }
    )

    filled = await _reporter(results, ofm).get_results()

    assert [result["branch"] for result in filled] == [
        "303B2",
        "303B1",
        "303B3",
    ]
    # исходные результаты и базовый номер скважины не меняются
    assert "branch" not in results[0]
    assert [result["well"] for result in filled] == ["303", "303", "303"]


@pytest.mark.asyncio
async def test_get_results_queries_each_object_and_date() -> None:
    results = [
        _file_result(reservoir="Вз", end_date=date(2026, 8, 1)),
        _file_result(reservoir="Тур", end_date=date(2026, 8, 1)),
        _file_result(reservoir="Вз", end_date=date(2026, 9, 1)),
    ]
    ofm = OfmWellTestMock()

    await _reporter(results, ofm).get_results()

    assert [call["key"] for call in ofm.calls] == ["branches"] * 3
    assert [call["cids"] for call in ofm.calls] == [
        ["Вз"],
        ["Тур"],
        ["Вз"],
    ]
    assert [call["end_date"] for call in ofm.calls] == [
        date(2026, 8, 1),
        date(2026, 8, 1),
        date(2026, 9, 1),
    ]
    assert all(call["fields"] == ["Котовское"] for call in ofm.calls)
    assert all(call["well"] == "303" for call in ofm.calls)


@pytest.mark.asyncio
async def test_get_results_falls_back_to_base_well() -> None:
    results = [_file_result()]

    filled = await _reporter(results, OfmWellTestMock()).get_results()

    assert filled[0]["branch"] == "303"
    assert filled[0]["well"] == "303"


def test_history_branch_keeps_well_layer_and_branch_separate() -> None:
    resolved = _resolve_history_branches(
        _history(_history_row()), _perfs(_perf(branch="303B1"))
    )

    assert resolved["branch"].to_list() == ["303B1"]
    assert resolved["well"].to_list() == ["303"]
    assert resolved["layer"].to_list() == ["Вз"]


def test_history_branch_respects_close_date() -> None:
    # Закрытый ствол лексикографически больше открытого: без фильтра
    # по close_date был бы выбран 303B2, поэтому проверка отличима.
    resolved = _resolve_history_branches(
        _history(_history_row(end_date=date(2021, 1, 1))),
        _perfs(
            _perf(
                branch="303B2",
                comp_date=date(2010, 1, 1),
                close_date=date(2015, 1, 1),
            ),
            _perf(branch="303B1", comp_date=date(2016, 1, 1)),
        ),
    )

    assert resolved["branch"].to_list() == ["303B1"]


def test_history_branch_ignores_interval_after_test_date() -> None:
    resolved = _resolve_history_branches(
        _history(_history_row(end_date=date(2019, 1, 1))),
        _perfs(_perf(branch="303B1", comp_date=date(2020, 1, 1))),
    )

    assert resolved["branch"].to_list() == ["303"]


def test_history_branch_uses_open_interval() -> None:
    resolved = _resolve_history_branches(
        _history(_history_row(end_date=date(2025, 6, 1))),
        _perfs(_perf(branch="303B3", close_date=None)),
    )

    assert resolved["branch"].to_list() == ["303B3"]


def test_history_branch_picks_lexicographic_max() -> None:
    resolved = _resolve_history_branches(
        _history(_history_row()),
        _perfs(
            _perf(branch="303"),
            _perf(branch="303B1"),
            _perf(branch="303B2"),
        ),
    )

    assert resolved["branch"].to_list() == ["303B2"]


def test_history_branch_without_perf_falls_back_to_well() -> None:
    resolved = _resolve_history_branches(_history(_history_row()), _perfs())

    assert resolved["branch"].to_list() == ["303"]


def test_history_branch_resolves_per_reservoir_and_falls_back() -> None:
    # Ствол подбирается по ключу (месторождение, скважина, объект):
    # перфорация есть только для «Вз», поэтому «Тур» откатывается
    # на базовую скважину, а не подхватывает ствол другого объекта.
    resolved = _resolve_history_branches(
        _history(
            _history_row(layer="Вз", reservoir="Вз"),
            _history_row(layer="Тур", reservoir="Тур"),
        ),
        _perfs(_perf(branch="303B1", reservoir="Вз")),
    )

    assert resolved["branch"].to_list() == ["303B1", "303"]
    assert resolved["layer"].to_list() == ["Вз", "Тур"]


def test_history_branch_does_not_duplicate_rows() -> None:
    history = _history(
        _history_row(end_date=date(2021, 1, 1)),
        _history_row(end_date=date(2025, 6, 1)),
    )
    resolved = _resolve_history_branches(
        history,
        _perfs(
            _perf(branch="303B1", comp_date=date(2010, 1, 1)),
            _perf(branch="303B1", comp_date=date(2011, 1, 1)),
            _perf(branch="303B2", comp_date=date(2012, 1, 1)),
        ),
    )

    assert resolved.shape[0] == 2
    assert resolved["branch"].to_list() == ["303B2", "303B2"]
    assert resolved["end_date"].to_list() == [
        date(2021, 1, 1),
        date(2025, 6, 1),
    ]


def test_history_branch_empty_frame_keeps_columns() -> None:
    resolved = _resolve_history_branches(_history(), _perfs())

    assert resolved.empty
    assert list(resolved.columns) == [*_HISTORY_COLUMNS, "branch"]
    assert resolved.shape == (0, len(_HISTORY_COLUMNS) + 1)


def test_concat_tests_keeps_history_and_current_branch() -> None:
    df = _concat_tests(
        _history(_history_row()),
        [_current_result()],
        _perfs(_perf(branch="303B1")),
    )

    assert df["branch"].to_list() == ["303B1", "303B2"]
    assert df["well"].to_list() == ["303", "303"]
    assert df["layer"].iloc[0] == "Вз"
    assert pd.isna(df["layer"].iloc[1])


def test_concat_tests_empty_history_keeps_columns() -> None:
    df = _concat_tests(_history(), [_current_result()], _perfs())

    assert df.shape == (1, len(_HISTORY_COLUMNS) + 1)
    assert df["branch"].iat[0] == "303B2"


@pytest.mark.asyncio
async def test_read_all_orchestrates_history_and_related_data() -> None:
    history = LocalWellTestMock(
        _history(
            _history_row(end_date=date(2024, 3, 1)),
            _history_row(end_date=date(2025, 9, 1)),
        )
    )
    ofm = OfmWellTestMock()
    reporter = WellTestReporter(
        history=history,
        results=FileWellTestMock([]),
        ofm=ofm,
    )

    dfs = await reporter.read_all(
        results=[_current_result()],
        gtm_period=12,
        gdis_period=5,
        radius=1.0,
    )

    assert set(dfs) == {
        "gtms",
        "tests",
        "perfs",
        "neighbs",
        "neighb_tests",
        "pvt",
    }
    assert dfs["tests"].equals(history.tests)
    assert len(dfs["perfs"]) == 2
    assert list(dfs["perfs"].columns) == list(PERF_COLUMNS)
    assert set(dfs["perfs"]["branch"]) == {"W1B1", "W1B2"}

    perfs_call = next(call for call in ofm.calls if call["key"] == "perfs")
    assert perfs_call["fields"] == ["Котовское"]
    assert perfs_call["wells"] == ["303"]
    assert perfs_call["cids"] == ["Вз"]
    assert perfs_call["history_start"] == date(2024, 3, 1)

    gtm_call = next(call for call in history.calls if call["key"] == "gtm")
    assert gtm_call["field"] == "Котовское"
    assert gtm_call["well"] == "303"
    assert gtm_call["date_from"] == date(2025, 8, 1)
    assert gtm_call["date_to"] == date(2026, 8, 1)

    gdis_call = next(call for call in history.calls if call["key"] == "gdis")
    assert gdis_call["field"] == "Котовское"
    assert gdis_call["well"] == "303"
    assert gdis_call["reservoirs"] == ["Вз"]
    assert gdis_call["report_date"] == date(2026, 8, 1)

    neighb_call = next(
        call for call in history.calls if call["key"] == "neighbs"
    )
    assert neighb_call["uids"] == ["F1W1R1"]
    assert neighb_call["date_from"] == date(2021, 8, 1)
    assert neighb_call["report_date"] == date(2026, 8, 1)


@pytest.mark.asyncio
async def test_read_all_skips_perfs_for_empty_history() -> None:
    history = LocalWellTestMock(_history())
    ofm = OfmWellTestMock()
    reporter = WellTestReporter(
        history=history,
        results=FileWellTestMock([]),
        ofm=ofm,
    )

    dfs = await reporter.read_all(
        results=[_current_result()],
        gtm_period=12,
        gdis_period=5,
        radius=1.0,
    )

    assert list(dfs["perfs"].columns) == list(PERF_COLUMNS)
    assert all(call["key"] != "perfs" for call in ofm.calls)


def test_process_data_writes_branches_and_filters_report_sheet(
    tmp_path: Path,
    well_test_template: Path,
    well_test_arrow: Path,
) -> None:
    history = _history(
        _history_row(end_date=date(2024, 3, 1)),
        _history_row(end_date=date(2025, 9, 1)),
    )
    perfs = _perfs(
        _perf(
            branch="303B1",
            comp_date=date(2010, 1, 1),
            close_date=date(2024, 6, 1),
        ),
        _perf(branch="303B2", comp_date=date(2024, 6, 2)),
    )
    dfs = _report_dfs(history, perfs, _gtms(_gtm_row()))

    wb, source_history = _run_report(
        tmp_path,
        dfs,
        [_current_result(branch="303B2")],
        well_test_template,
        well_test_arrow,
    )

    # «Лист1»: все ГДИС со стволом в столбце B
    ws = wb["Лист1"]
    assert [ws[f"B{row}"].value for row in range(2, 5)] == [
        "303B1 (Вз)",
        "303B2 (Вз)",
        "303B2",
    ]
    assert [ws[f"C{row}"].value for row in range(2, 5)] == ["Вз"] * 3
    assert ws["B5"].value in (None, " ")
    # исходный набор, well и layer не изменяются, branch не добавляется
    assert source_history["well"].to_list() == ["303", "303"]
    assert source_history["layer"].to_list() == ["Вз", "Вз"]
    assert "branch" not in source_history

    # «отчет»: только история текущего ствола с базовым номером в B
    ws = wb["отчет"]
    assert ws["B10"].value == "303 (Вз)"
    assert ws["C10"].value == "КВД"
    assert ws["D10"].value.date() == date(2025, 9, 1)
    # строки другого ствола (2024-03-01) на листе нет
    assert ws["D11"].value.date() == date(2025, 12, 1)
    assert ws["B11"].value == 303
    assert ws["C11"].value == "ГТМ"
    assert ws["D12"].value.date() == date(2026, 8, 1)
    assert ws["B12"].value == 303
    assert ws["C12"].value == "КВД"

    # столбец M: давление для ГДИС, пусто и без оформления у ГТМ
    assert ws["M10"].value == 100.0
    assert ws["M12"].value == 100.0
    _assert_column_m_blank(ws, range(11, 12))

    # график по-прежнему строится по датам D и давлениям M
    plot = next(
        series
        for series in ws._charts[0].series  # type: ignore[attr-defined]
        if series.title.value == "Pпл"
    )
    assert plot.xVal.numRef.f == "'отчет'!$D$10:$D$55"
    assert plot.yVal.numRef.f == "'отчет'!$M$10:$M$55"


def test_process_data_without_perforations_uses_base_well(
    tmp_path: Path,
    well_test_template: Path,
    well_test_arrow: Path,
) -> None:
    history = _history(
        _history_row(end_date=date(2024, 3, 1)),
        _history_row(end_date=date(2025, 9, 1)),
    )
    dfs = _report_dfs(history, _perfs(), _gtms(_gtm_row()))

    wb, _ = _run_report(
        tmp_path,
        dfs,
        [_current_result(branch="303")],
        well_test_template,
        well_test_arrow,
    )

    # «Лист1»: базовая скважина, история с суффиксом пласта
    ws = wb["Лист1"]
    assert [ws[f"B{row}"].value for row in range(2, 5)] == [
        "303 (Вз)",
        "303 (Вз)",
        "303",
    ]
    assert ws["B5"].value in (None, " ")

    # «отчет»: история не исчезает, базовый номер в B, ГТМ добавляются
    ws = wb["отчет"]
    assert ws["B10"].value == "303 (Вз)"
    assert ws["D10"].value.date() == date(2024, 3, 1)
    assert ws["B11"].value == "303 (Вз)"
    assert ws["D11"].value.date() == date(2025, 9, 1)
    assert ws["B12"].value == 303
    assert ws["C12"].value == "ГТМ"
    assert ws["D12"].value.date() == date(2025, 12, 1)
    assert ws["B13"].value == 303
    assert ws["C13"].value == "КВД"
    assert ws["D13"].value.date() == date(2026, 8, 1)

    # столбец M: давление у ГДИС, пусто и без оформления у ГТМ
    assert ws["M10"].value == 100.0
    assert ws["M11"].value == 100.0
    assert ws["M13"].value == 100.0
    _assert_column_m_blank(ws, range(12, 13))
