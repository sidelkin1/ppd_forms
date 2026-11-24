"""Проверка SQL-выгрузки дебитов ТР/МЭР без подключения к Oracle.

Модели OFM подключаются через ``DeferredReflection``, поэтому колонки
добавляются в метаданные тестами вручную: запросы строятся и
компилируются, но не исполняются. Семантика проверяется по форме
запроса, а прогон на реальных данных OFM выполняется отдельно.
"""

from typing import Any

import pytest
from sqlalchemy import Column, Date, Integer, Numeric, String
from sqlalchemy.dialects import oracle
from sqlalchemy.sql.expression import Select
from sqlalchemy.sql.selectable import CompoundSelect

from app.infrastructure.db.dao.sql.reporters.querysets.owc_resp import (
    mer_rates,
    rates,
    reservoirs,
    tr_rates,
)
from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    TmpWellNgOis2,
    TmpWellOpOis2,
    WellHdr,
    WellMonthHist,
)

_COLUMNS: dict[Any, dict[str, Any]] = {
    WellHdr: {
        "uwi": String(),
        "parent_uwi": String(),
        "well_name": String(),
        "field": String(),
    },
    WellMonthHist: {
        "uwi": String(),
        "layer_id": String(),
        "start_date": Date(),
        "oil": Numeric(),
        "water": Numeric(),
        "act_time": Numeric(),
        "oil_v": Numeric(),
        "water_v": Numeric(),
    },
    TmpWellOpOis2: {
        "uwi": String(),
        "official_date": Date(),
        "layer_id": String(),
        "oil_rate": Numeric(),
        "liq_rate": Numeric(),
        "water_cut": Numeric(),
        "flow_pressure": Numeric(),
    },
    TmpWellNgOis2: {
        "uwi": String(),
        "official_date": Date(),
        "layer_id": String(),
        "intake": Numeric(),
        "layer_flow_pressure": Numeric(),
    },
    DictG: {
        "id": Integer(),
        "mr": Integer(),
        "description": String(),
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


def _compiled(query: Select | CompoundSelect) -> Any:
    return query.compile(dialect=oracle.dialect())


def _sql(query: Select | CompoundSelect) -> str:
    return str(_compiled(query))


def test_reservoir_names_use_dictionary_description() -> None:
    sql = _sql(reservoirs.select_reservoir_names())

    assert "lower(codes.dict_g.description)" in sql
    assert "codes.dict_g.id = :reservoir_id" in sql
    assert "codes.dict_g.mr = to_char(:reservoir_id)" in sql
    assert "UNION" in sql


def test_mer_rates_convert_hours_to_days() -> None:
    compiled = _compiled(mer_rates.select_mer_rates())
    sql = str(compiled)

    assert 24 in compiled.params.values()
    assert "sum(udmurtneft_n.well_month_hist.act_time)" in sql
    assert "END AS oil_rate" in sql


def test_mer_rates_use_last_date_and_base_well() -> None:
    sql = _sql(mer_rates.select_mer_rates())

    assert (
        "coalesce(udmurtneft_n.well_hdr.parent_uwi, "
        "udmurtneft_n.well_hdr.uwi)" in sql
    )
    assert "udmurtneft_n.well_month_hist.start_date <= :on_date" in sql
    assert (
        "start_date = (SELECT max("
        "udmurtneft_n.well_month_hist.start_date)" in sql
    )
    assert "SELECT :reservoir_id AS reservoir" in sql
    assert "codes.dict_g.mr = to_char(:reservoir_id)" in sql
    # агрегаты без GROUP BY всегда дают одну строку
    assert "GROUP BY" not in sql


def test_mer_rates_fall_back_from_volume_to_mass() -> None:
    compiled = _compiled(mer_rates.select_mer_rates())
    sql = str(compiled)

    assert "coalesce(udmurtneft_n.well_month_hist.oil_v" in sql
    assert "coalesce(udmurtneft_n.well_month_hist.water_v" in sql
    assert "coalesce(udmurtneft_n.well_month_hist.oil," in sql
    assert "coalesce(udmurtneft_n.well_month_hist.water," in sql
    # два CASE для жидкости/обводненности плюс CASE для дебита нефти
    assert sql.count("CASE WHEN") >= 3
    assert 100 in compiled.params.values()


def test_tr_rates_combine_oil_and_injection_funds() -> None:
    compiled = _compiled(tr_rates.select_tr_rates())
    sql = str(compiled)

    assert "udmurtneft_n.tmp_wellop_ois2" in sql
    assert "udmurtneft_n.tmp_wellng_ois2" in sql
    assert "UNION ALL" in sql
    assert "NULL AS oil_rate" in sql
    assert "udmurtneft_n.tmp_wellng_ois2.intake AS liq_rate" in sql
    assert "udmurtneft_n.tmp_wellng_ois2.layer_flow_pressure AS bhp" in sql
    assert 100 in compiled.params.values()


def test_tr_rates_choose_latest_date_with_oil_priority() -> None:
    sql = _sql(tr_rates.select_tr_rates())

    assert (
        "row_number() OVER (ORDER BY tr_rows.official_date DESC, "
        "tr_rows.src, tr_rows.layer_id)" in sql
    )
    assert "tr_ranked.rn = :rn_1" in sql


def test_tr_rates_filter_base_uwi_and_reservoir_names() -> None:
    sql = _sql(tr_rates.select_tr_rates())

    assert (
        "udmurtneft_n.tmp_wellop_ois2.uwi IN (SELECT coalesce("
        "udmurtneft_n.well_hdr.parent_uwi, "
        "udmurtneft_n.well_hdr.uwi)" in sql
    )
    assert (
        "lower(udmurtneft_n.tmp_wellop_ois2.layer_id) IN (SELECT "
        "lower(codes.dict_g.description)" in sql
    )
    assert "udmurtneft_n.tmp_wellop_ois2.official_date <= :on_date" in sql


def test_rates_prefer_later_source_and_tr_on_tie() -> None:
    sql = _sql(rates.select_rates())
    outer = sql.split("FROM (SELECT max(", 1)[0]

    assert "LEFT OUTER JOIN" in sql
    assert 'tr_rates."date" IS NOT NULL' in outer
    assert 'mer_rates."date" IS NULL' in outer
    assert 'tr_rates."date" >= mer_rates."date"' in outer
    assert 'tr_rates."date" < mer_rates."date"' in outer
    # нет ELSE: при отсутствии обоих источников все значения NULL
    assert " ELSE " not in outer
    for column in ("oil_rate", "liq_rate", "watercut", "tr_bhp"):
        assert f"END AS {column}" in outer


def test_rates_keep_bhp_from_tr_only() -> None:
    sql = _sql(rates.select_rates())
    outer = sql.split("FROM (SELECT max(", 1)[0]
    bhp = outer.split("END AS tr_bhp", 1)[0].rsplit("CASE", 1)[1]

    assert "THEN tr_rates.tr_bhp" in bhp
    assert "mer_rates.tr_bhp" not in outer
