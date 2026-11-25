"""Ствол текущего ГДИС: SQL-выгрузка и заполнение результатов.

Модели OFM подключаются через ``DeferredReflection``, поэтому колонки
добавляются в метаданные тестами вручную: запросы строятся и
компилируются, но не исполняются. Работа с Oracle проверяется отдельно.
"""

from datetime import date
from typing import Any, cast

import pandas as pd
import pytest
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.dialects import oracle
from sqlalchemy.sql.expression import Select

from app.core.models.dto import WellTestResult
from app.core.services.reports.well_test import (
    _concat_tests,
    _resolve_history_branches,
)
from app.infrastructure.db.dao.complex.reporters.well_test import (
    WellTestReporter,
)
from app.infrastructure.db.dao.sql.reporters.ofm_well_test import (
    PERF_COLUMNS,
)
from app.infrastructure.db.dao.sql.reporters.querysets.well_test import (
    branches,
    perfs,
)
from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    WellHdr,
    WellPerforations,
)
from tests.mocks.reporters import OfmWellTestMock

_STRING_COLUMNS = ("uwi", "parent_uwi", "well_name", "field")

_COLUMNS: dict[Any, dict[str, Any]] = {
    WellHdr: {name: String() for name in _STRING_COLUMNS},
    WellPerforations: {
        "uwi": String(),
        "comp_date": Date(),
        "close_date": Date(),
        "layer_id": String(),
    },
    DictG: {
        "id": Integer(),
        "mr": Integer(),
        "description": String(),
        "sdes": String(),
    },
}


def _add_column(model: Any, name: str, type_: Any) -> None:
    table = model.__table__
    column = table.c.get(name)
    if column is None:
        column = Column(name, type_)
        table.append_column(column)
    setattr(model, name, column)


@pytest.fixture(autouse=True, scope="module")
def _ofm_columns() -> None:
    for model, columns in _COLUMNS.items():
        for name, type_ in columns.items():
            _add_column(model, name, type_)


def _compiled(query: Select) -> Any:
    return query.compile(dialect=oracle.dialect())


def _sql(query: Select) -> str:
    return str(_compiled(query))


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


class _FileResultsMock:
    def __init__(self, results: list[WellTestResult]) -> None:
        self.results = results

    async def get_results(self) -> list[WellTestResult]:
        return self.results


class _OfmBranchMock:
    """Отдаёт ствол по ключу (скважина, объект), иначе пустой набор."""

    def __init__(self, found: dict[tuple[str, str], str]) -> None:
        self.found = found
        self.calls: list[dict[str, Any]] = []

    async def read_one(
        self, *, key: str | None = None, **params: Any
    ) -> pd.DataFrame:
        self.calls.append({"key": key, **params})
        branch = self.found.get((params["well"], params["cids"][0]))
        if branch is None:
            return pd.DataFrame(columns=["branch"])
        return pd.DataFrame({"branch": [branch]})


def _reporter(
    results: list[WellTestResult], ofm: _OfmBranchMock
) -> WellTestReporter:
    return WellTestReporter(
        history=cast(Any, None),
        results=cast(Any, _FileResultsMock(results)),
        ofm=cast(Any, ofm),
    )


def test_branch_query_resolves_field_and_object() -> None:
    sql = _sql(branches.select_well_branch())

    # месторождение — по названию из справочника, как в isobar
    assert "codes.dict_g.description IN" in sql
    # объект — через layer_id с ИЖВ-резолвом mr
    assert "udmurtneft_n.well_perforations.layer_id IN" in sql
    assert "decode(mapped_object.mr" in sql
    assert "replace(base_object.sdes" in sql


def test_branch_query_keeps_open_perforations() -> None:
    sql = _sql(branches.select_well_branch())

    assert "comp_date <= :end_date" in sql
    assert "close_date IS NULL" in sql
    assert "close_date >= :end_date" in sql
    assert "BETWEEN" not in sql.upper()


def test_branch_query_parameter_set() -> None:
    compiled = _compiled(branches.select_well_branch())

    assert {"well", "fields", "cids", "end_date"} <= set(compiled.params)
    assert compiled.params["replace_1"] == "(Руд)"
    assert compiled.params["replace_2"] == ""


def test_branch_query_returns_max_well_name() -> None:
    sql = _sql(branches.select_well_branch())

    # лексикографический максимум ствола и его отображаемое имя
    assert "max(perf_branch.uwi)" in sql
    assert ".well_name AS branch" in sql
    # fallback к базовой скважине
    assert "coalesce(" in sql
    assert "coalesce(perf_branch.parent_uwi, perf_branch.uwi)" in sql


@pytest.mark.asyncio
async def test_get_results_fills_branch_per_object() -> None:
    results = [
        _file_result(reservoir="Вз"),
        _file_result(reservoir="Тур"),
    ]
    ofm = _OfmBranchMock({("303", "Вз"): "303B2", ("303", "Тур"): "303B1"})

    filled = await _reporter(results, ofm).get_results()

    assert [result["branch"] for result in filled] == ["303B2", "303B1"]
    # исходные результаты и базовый номер скважины не меняются
    assert "branch" not in results[0]
    assert [result["well"] for result in filled] == ["303", "303"]


@pytest.mark.asyncio
async def test_get_results_queries_each_object_and_date() -> None:
    results = [
        _file_result(reservoir="Вз", end_date=date(2026, 8, 1)),
        _file_result(reservoir="Тур", end_date=date(2026, 8, 1)),
    ]
    ofm = _OfmBranchMock({})

    await _reporter(results, ofm).get_results()

    assert [call["key"] for call in ofm.calls] == ["branches", "branches"]
    assert [call["cids"] for call in ofm.calls] == [["Вз"], ["Тур"]]
    assert ofm.calls[0]["fields"] == ["Котовское"]
    assert ofm.calls[0]["well"] == "303"
    assert ofm.calls[0]["end_date"] == date(2026, 8, 1)


@pytest.mark.asyncio
async def test_get_results_falls_back_to_base_well() -> None:
    results = [_file_result()]

    filled = await _reporter(results, _OfmBranchMock({})).get_results()

    assert filled[0]["branch"] == "303"
    assert filled[0]["well"] == "303"


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
)

_PERF_COLUMNS = (
    "field",
    "well",
    "reservoir",
    "branch",
    "comp_date",
    "close_date",
)


def _history_row(
    *,
    well: str = "303 (Вз)",
    reservoir: str = "Вз",
    end_date: date = date(2025, 6, 1),
) -> dict[str, Any]:
    return {
        "field": "Котовское",
        "well": well,
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
    return pd.DataFrame(list(rows), columns=list(_PERF_COLUMNS))


def _current_result(branch: str = "303B2") -> WellTestResult:
    return cast(WellTestResult, {**_file_result(), "branch": branch})


def test_perfs_query_resolves_field_and_object() -> None:
    sql = _sql(perfs.select_well_perfs())

    assert "codes.dict_g.description IN" in sql
    assert "udmurtneft_n.well_perforations.layer_id IN" in sql
    assert "decode(" in sql
    assert "replace(" in sql


def test_perfs_query_joins_branch_to_base_well() -> None:
    sql = _sql(perfs.select_well_perfs())

    assert "coalesce(" in sql
    assert "parent_uwi" in sql
    # отображаемые колонки истории
    for label in ("field", "well", "reservoir", "branch"):
        assert f"AS {label}" in sql
    assert "AS comp_date" in sql
    assert "AS close_date" in sql


def test_perfs_query_keeps_open_intervals() -> None:
    sql = _sql(perfs.select_well_perfs())

    assert "close_date IS NULL" in sql
    assert "close_date >= :history_start" in sql
    assert "BETWEEN" not in sql.upper()


def test_perfs_query_parameter_set() -> None:
    compiled = _compiled(perfs.select_well_perfs())

    assert {"fields", "wells", "cids", "history_start"} <= set(compiled.params)
    assert compiled.params["replace_1"] == "(Руд)"
    assert compiled.params["replace_2"] == ""


def test_history_branch_adds_layer_suffix() -> None:
    resolved = _resolve_history_branches(
        _history(_history_row()), _perfs(_perf(branch="303B1"))
    )

    assert resolved["branch"].to_list() == ["303B1 (Вз)"]
    assert resolved["well"].to_list() == ["303 (Вз)"]


def test_history_branch_respects_close_date() -> None:
    resolved = _resolve_history_branches(
        _history(_history_row(end_date=date(2021, 1, 1))),
        _perfs(
            _perf(
                branch="303B1",
                comp_date=date(2010, 1, 1),
                close_date=date(2015, 1, 1),
            ),
            _perf(branch="303B2", comp_date=date(2016, 1, 1)),
        ),
    )

    assert resolved["branch"].to_list() == ["303B2 (Вз)"]


def test_history_branch_ignores_interval_after_test_date() -> None:
    resolved = _resolve_history_branches(
        _history(_history_row(end_date=date(2019, 1, 1))),
        _perfs(_perf(branch="303B1", comp_date=date(2020, 1, 1))),
    )

    assert resolved["branch"].to_list() == ["303 (Вз)"]


def test_history_branch_uses_open_interval() -> None:
    resolved = _resolve_history_branches(
        _history(_history_row(end_date=date(2025, 6, 1))),
        _perfs(_perf(branch="303B3", close_date=None)),
    )

    assert resolved["branch"].to_list() == ["303B3 (Вз)"]


def test_history_branch_picks_lexicographic_max() -> None:
    resolved = _resolve_history_branches(
        _history(_history_row()),
        _perfs(
            _perf(branch="303"),
            _perf(branch="303B1"),
            _perf(branch="303B2"),
        ),
    )

    assert resolved["branch"].to_list() == ["303B2 (Вз)"]


def test_history_branch_without_perf_falls_back_to_well() -> None:
    resolved = _resolve_history_branches(_history(_history_row()), _perfs())

    assert resolved["branch"].to_list() == ["303 (Вз)"]


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
    assert resolved["branch"].to_list() == ["303B2 (Вз)", "303B2 (Вз)"]
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

    assert df["branch"].to_list() == ["303B1 (Вз)", "303B2"]
    assert df["well"].to_list() == ["303 (Вз)", "303"]


def test_concat_tests_empty_history_keeps_columns() -> None:
    df = _concat_tests(_history(), [_current_result()], _perfs())

    assert df.shape == (1, len(_HISTORY_COLUMNS) + 1)
    assert df["branch"].iat[0] == "303B2"


class _HistoryReadMock:
    def __init__(self, tests: pd.DataFrame) -> None:
        self.tests = tests
        self.calls: list[dict[str, Any]] = []

    async def read_one(
        self, *, key: str | None = None, **params: Any
    ) -> pd.DataFrame:
        self.calls.append({"key": key, **params})
        if key == "gdis":
            return self.tests
        return pd.DataFrame()


@pytest.mark.asyncio
async def test_read_all_loads_history_perforations() -> None:
    history = _HistoryReadMock(
        _history(
            _history_row(end_date=date(2024, 3, 1)),
            _history_row(end_date=date(2025, 9, 1)),
        )
    )
    ofm = OfmWellTestMock()
    reporter = WellTestReporter(
        history=cast(Any, history),
        results=cast(Any, None),
        ofm=cast(Any, ofm),
    )

    dfs = await reporter.read_all(
        results=[_current_result()],
        gtm_period=12,
        gdis_period=5,
        radius=1.0,
    )

    assert len(dfs["perfs"]) == 2
    perfs_call = next(call for call in ofm.calls if call["key"] == "perfs")
    assert perfs_call["fields"] == ["Котовское"]
    assert perfs_call["wells"] == ["303"]
    assert perfs_call["cids"] == ["Вз"]
    assert perfs_call["history_start"] == date(2024, 3, 1)


@pytest.mark.asyncio
async def test_read_all_skips_perfs_for_empty_history() -> None:
    history = _HistoryReadMock(_history())
    ofm = OfmWellTestMock()
    reporter = WellTestReporter(
        history=cast(Any, history),
        results=cast(Any, None),
        ofm=cast(Any, ofm),
    )

    dfs = await reporter.read_all(
        results=[_current_result()],
        gtm_period=12,
        gdis_period=5,
        radius=1.0,
    )

    assert list(dfs["perfs"].columns) == list(PERF_COLUMNS)
    assert all(call["key"] != "perfs" for call in ofm.calls)
