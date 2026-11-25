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
from app.infrastructure.db.dao.complex.reporters.well_test import (
    WellTestReporter,
)
from app.infrastructure.db.dao.sql.reporters.querysets.well_test import (
    branches,
)
from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    WellHdr,
    WellPerforations,
)

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
