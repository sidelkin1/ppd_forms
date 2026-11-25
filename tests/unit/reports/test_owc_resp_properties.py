"""Проверка SQL-выгрузки свойств owc_resp без подключения к Oracle.

Модели OFM подключаются через ``DeferredReflection``, поэтому колонки
добавляются в метаданные тестами вручную: запросы строятся и
компилируются, но не исполняются. Семантика проверяется по форме
запроса, а прогон на реальных данных OFM выполняется отдельно.
"""

from typing import Any

import pytest
from sqlalchemy import Column, Date, Integer, Numeric, String
from sqlalchemy.dialects import oracle
from sqlalchemy.sql.expression import ScalarSelect, Select

from app.infrastructure.db.dao.sql.reporters.querysets.owc_resp import (
    branches,
    perfs,
    properties,
)
from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    Reservoir2,
    ResPty,
    TmpWellNgOis2,
    TmpWellOpOis2,
    WellHdr,
    WellHdrPty,
    WellMonthHist,
    WellMonthHistPty,
    WellPerforations,
    WellStockHist,
    WellStockHistExt,
)

_STRING_COLUMNS = (
    "uwi",
    "parent_uwi",
    "well_name",
    "field",
    "elevation",
    "operator",
    "agent",
    "rig_no",
    "hole_direction",
    "district",
)

_PVT_COLUMNS = (
    "abs_depth_owc",
    "separated_oil_density",
    "water_density",
    "reservoir_s",
    "initial_layer_pressure",
    "bubble_point_pressure",
    "gas_factor",
    "layer_oil_dyn_viscosity",
    "layer_water_dyn_viscosity",
    "oil_compressibility",
    "layer_oil_density",
    "layer_temperature",
    "layer_oil_compressibility",
    "water_compressibility",
)

_COLUMNS: dict[Any, dict[str, Any]] = {
    WellHdr: {name: String() for name in _STRING_COLUMNS},
    Reservoir2: {
        "reservoir_id": String(),
        "field_code": String(),
        "district": String(),
        "existence_type": String(),
        "reservoir_s": String(),
    },
    ResPty: {name: Numeric() for name in _PVT_COLUMNS},
    WellPerforations: {
        "top": Numeric(),
        "base": Numeric(),
        "comp_date": Date(),
        "close_date": Date(),
        "layer_id": String(),
        "uwi": String(),
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
        "rec_id": Integer(),
    },
    WellMonthHistPty: {
        "wmh_id": Integer(),
        "parameter_id": Integer(),
        "num_val": Numeric(),
    },
    WellStockHistExt: {
        "status_date": Date(),
        "ora1": String(),
        "ora2": String(),
        "ora3": String(),
        "bs1": String(),
        "bs2": String(),
        "bs3": String(),
    },
    WellStockHist: {
        "status_date": Date(),
        "uwi": String(),
        "prod_class": String(),
        "prod_method": String(),
        "status": String(),
    },
    DictG: {
        "id": Integer(),
        "mr": Integer(),
        "description": String(),
        "code": String(),
    },
    WellHdrPty: {
        "uwi": String(),
        "property_id": String(),
        "num_val": Numeric(),
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


def _compiled(query: Select | ScalarSelect) -> Any:
    return query.compile(dialect=oracle.dialect())


def _sql(query: Select | ScalarSelect) -> str:
    return str(_compiled(query))


def test_properties_include_current_rates() -> None:
    sql = _sql(properties.select_properties())

    for column in ("oil_rate", "liq_rate", "watercut"):
        assert f"END AS {column}" in sql
    assert "tr_rates.tr_bhp AS tr_bhp" in sql
    assert "rates.oil_rate" in sql
    assert "rates.liq_rate" in sql
    assert "rates.watercut" in sql
    assert "rates.tr_bhp" in sql


def test_properties_rates_subquery_keeps_row() -> None:
    sql = _sql(properties.select_properties())

    # МЭР всегда даёт строку, ТР присоединяется снаружи — при отсутствии
    # обоих источников свойства скважины не теряются.
    assert "mer_rates LEFT OUTER JOIN" in sql
    assert "LEFT OUTER JOIN rates" not in sql


def test_properties_include_perforations() -> None:
    sql = _sql(properties.select_properties())

    assert "min(udmurtneft_n.well_perforations.top)" in sql
    assert "max(udmurtneft_n.well_perforations.base)" in sql
    assert "AS top_perf" in sql
    assert "AS bottom_perf" in sql


def test_properties_include_pvt_fields() -> None:
    sql = _sql(properties.select_properties())

    assert "udmurtneft_n.res_pty.initial_layer_pressure AS init_resp" in sql
    assert "udmurtneft_n.res_pty.bubble_point_pressure AS bubble_resp" in sql
    assert "udmurtneft_n.res_pty.gas_factor" in sql
    assert (
        "udmurtneft_n.res_pty.layer_oil_dyn_viscosity AS oil_viscosity" in sql
    )
    assert (
        "udmurtneft_n.res_pty.layer_water_dyn_viscosity AS water_viscosity"
        in sql
    )
    # в БД колонка названа oil_compressibility, но хранит FVF
    assert "udmurtneft_n.res_pty.oil_compressibility AS oil_fvf" in sql
    assert (
        "udmurtneft_n.res_pty.layer_oil_density AS reservoir_oil_density"
        in sql
    )
    assert (
        "udmurtneft_n.res_pty.layer_temperature AS reservoir_temperature"
        in sql
    )


def test_properties_separate_surface_and_reservoir_density() -> None:
    sql = _sql(properties.select_properties())

    assert (
        "udmurtneft_n.res_pty.separated_oil_density AS surface_oil_density"
        in sql
    )
    assert (
        "udmurtneft_n.res_pty.layer_oil_density AS reservoir_oil_density"
        in sql
    )
    assert " AS oil_density" not in sql


def test_properties_scale_compressibility() -> None:
    compiled = _compiled(properties.select_properties())
    sql = str(compiled)

    assert 0.00001 in compiled.params.values()
    assert (
        "AS oil_compressibility" in sql
        and "udmurtneft_n.res_pty.layer_oil_compressibility" in sql
    )
    assert (
        "AS water_compressibility" in sql
        and "udmurtneft_n.res_pty.water_compressibility" in sql
    )


def test_properties_join_field_code() -> None:
    sql = _sql(properties.select_properties())

    assert "codes.dict_g.id = udmurtneft_n.well_hdr.field" in sql
    assert "max(codes.dict_g.code)" in sql
    assert "AS field_code" in sql


def test_properties_well_radius_by_property_id() -> None:
    compiled = _compiled(properties.select_properties())
    sql = str(compiled)

    assert "udmurtneft_n.well_hdr_pty.uwi = udmurtneft_n.well_hdr.uwi" in sql
    assert "udmurtneft_n.well_hdr_pty.property_id = :property_id_1" in sql
    assert "max(udmurtneft_n.well_hdr_pty.num_val)" in sql
    assert "AS well_radius" in sql
    assert "1071381" in compiled.params.values()


def test_branch_query_keeps_open_perforations() -> None:
    """Ствол ищется и по открытым интервалам (``close_date IS NULL``)."""
    sql = _sql(branches.select_well_branch())

    assert "max(udmurtneft_n.well_perforations.uwi)" in sql
    assert "udmurtneft_n.well_perforations.comp_date <= :on_date" in sql
    assert "udmurtneft_n.well_perforations.close_date IS NULL" in sql
    assert "udmurtneft_n.well_perforations.close_date >= :on_date" in sql
    assert "BETWEEN" not in sql.upper()
    # при отсутствии открытой перфорации остаётся базовая скважина
    assert sql.startswith("SELECT coalesce(")


def test_top_and_bottom_perf_use_same_filters() -> None:
    top = _sql(perfs.select_top_perf())
    bottom = _sql(perfs.select_bottom_perf())

    assert "min(udmurtneft_n.well_perforations.top)" in top
    assert "max(udmurtneft_n.well_perforations.base)" in bottom
    for sql in (top, bottom):
        assert (
            "udmurtneft_n.well_perforations.uwi = "
            "udmurtneft_n.well_hdr.uwi" in sql
        )
        assert "udmurtneft_n.well_perforations.layer_id IN" in sql
        assert "udmurtneft_n.well_perforations.comp_date <= :on_date" in sql
        assert "udmurtneft_n.well_perforations.close_date IS NULL" in sql
        assert "udmurtneft_n.well_perforations.close_date >= :on_date" in sql
