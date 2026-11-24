from sqlalchemy import bindparam, func, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    Reservoir2,
    ResPty,
    WellHdr,
    WellHdrPty,
)

from .branches import select_well_branch
from .density import select_water_density
from .perfs import select_bottom_perf, select_top_perf
from .rates import select_rates
from .stock import select_well_stock_hist
from .well_reservoir import select_well_reservoir_id

_WELL_RADIUS_PROPERTY_ID = "1071381"
_COMPRESSIBILITY_FACTOR = 0.00001


def _select_field_code():
    """Код месторождения из словаря по идентификатору месторождения."""
    return (
        select(func.max(DictG.code))
        .where(DictG.id == WellHdr.field)
        .scalar_subquery()
        .correlate(WellHdr.__table__)
    )


def _select_well_radius():
    """Радиус скважины; дубликаты сводятся к одному значению."""
    return (
        select(func.max(WellHdrPty.num_val))
        .where(
            WellHdrPty.uwi == WellHdr.uwi,
            WellHdrPty.property_id == _WELL_RADIUS_PROPERTY_ID,
        )
        .scalar_subquery()
        .correlate(WellHdr.__table__)
    )


def select_properties() -> Select:
    stock = select_well_stock_hist()
    rates = select_rates().subquery("rates")
    return select(
        func.udmurtneft_n.dg_des(bindparam("field_id")).label("field"),
        bindparam("well").label("well"),
        WellHdr.well_name.label("branch"),
        func.udmurtneft_n.dg_des(bindparam("reservoir_id")).label("reservoir"),
        bindparam("on_date").label("on_date"),
        _select_field_code().label("field_code"),
        WellHdr.elevation,
        func.abs(ResPty.abs_depth_owc).label("abs_depth_owc"),
        ResPty.separated_oil_density.label("surface_oil_density"),
        func.coalesce(select_water_density(), ResPty.water_density).label(
            "water_density"
        ),
        ResPty.initial_layer_pressure.label("init_resp"),
        ResPty.bubble_point_pressure.label("bubble_resp"),
        ResPty.gas_factor,
        ResPty.layer_oil_dyn_viscosity.label("oil_viscosity"),
        ResPty.layer_water_dyn_viscosity.label("water_viscosity"),
        # OIL_COMPRESSIBILITY фактически хранит объёмный коэффициент нефти
        ResPty.oil_compressibility.label("oil_fvf"),
        ResPty.layer_oil_density.label("reservoir_oil_density"),
        ResPty.layer_temperature.label("reservoir_temperature"),
        (_COMPRESSIBILITY_FACTOR * ResPty.layer_oil_compressibility).label(
            "oil_compressibility"
        ),
        (_COMPRESSIBILITY_FACTOR * ResPty.water_compressibility).label(
            "water_compressibility"
        ),
        select_top_perf().label("top_perf"),
        select_bottom_perf().label("bottom_perf"),
        _select_well_radius().label("well_radius"),
        rates.c.oil_rate,
        rates.c.liq_rate,
        rates.c.watercut,
        rates.c.tr_bhp,
        func.udmurtneft_n.dg_des(WellHdr.operator).label("region"),
        func.udmurtneft_n.dg_des(WellHdr.agent).label("workshop"),
        WellHdr.rig_no.label("pad"),
        func.udmurtneft_n.dg_des(WellHdr.hole_direction).label("wellbore"),
        func.udmurtneft_n.dg_des(stock.c.prod_class).label("well_mode"),
        func.udmurtneft_n.dg_sdes(stock.c.prod_method).label("well_lift"),
        func.udmurtneft_n.dg_sdes(stock.c.status).label("well_status"),
    ).where(
        WellHdr.uwi.in_(select_well_branch()),
        # пласт выбран по базовому id словаря, а в reservoir2 он записан
        # в кодировке месторождения — той, что числится за стволом
        Reservoir2.reservoir_id == select_well_reservoir_id(),
        Reservoir2.field_code == WellHdr.field,
        Reservoir2.district == WellHdr.district,
        Reservoir2.existence_type == "ACTUAL",
        ResPty.reservoir_s == Reservoir2.reservoir_s,
        stock.c.uwi == func.coalesce(WellHdr.parent_uwi, WellHdr.uwi),
    )
