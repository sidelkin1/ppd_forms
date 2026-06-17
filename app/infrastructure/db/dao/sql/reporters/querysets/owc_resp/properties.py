from sqlalchemy import bindparam, func, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.reflected import (
    Reservoir2,
    ResPty,
    WellHdr,
)

from .branches import select_well_branch
from .density import select_water_density
from .stock import select_well_stock_hist
from .top_perf import select_top_perf
from .watercut import select_watercut


def select_properties() -> Select:
    stock = select_well_stock_hist()
    return select(
        func.udmurtneft_n.dg_des(bindparam("field_id")).label("field"),
        bindparam("well").label("well"),
        WellHdr.well_name.label("branch"),
        func.udmurtneft_n.dg_des(bindparam("reservoir_id")).label("reservoir"),
        bindparam("on_date").label("on_date"),
        WellHdr.elevation,
        func.abs(ResPty.abs_depth_owc).label("abs_depth_owc"),
        ResPty.separated_oil_density.label("oil_density"),
        func.coalesce(select_water_density(), ResPty.water_density).label(
            "water_density"
        ),
        select_watercut().label("watercut"),
        select_top_perf().label("top_perf"),
        func.udmurtneft_n.dg_des(WellHdr.operator).label("region"),
        func.udmurtneft_n.dg_des(WellHdr.agent).label("workshop"),
        WellHdr.rig_no.label("pad"),
        func.udmurtneft_n.dg_des(WellHdr.hole_direction).label("wellbore"),
        func.udmurtneft_n.dg_des(stock.c.prod_class).label("well_mode"),
        func.udmurtneft_n.dg_sdes(stock.c.prod_method).label("well_lift"),
        func.udmurtneft_n.dg_sdes(stock.c.status).label("well_status"),
    ).where(
        WellHdr.uwi.in_(select_well_branch()),
        Reservoir2.reservoir_id == bindparam("reservoir_id"),
        Reservoir2.field_code == WellHdr.field,
        Reservoir2.district == WellHdr.district,
        Reservoir2.existence_type == "ACTUAL",
        ResPty.reservoir_s == Reservoir2.reservoir_s,
        stock.c.uwi == func.coalesce(WellHdr.parent_uwi, WellHdr.uwi),
    )
