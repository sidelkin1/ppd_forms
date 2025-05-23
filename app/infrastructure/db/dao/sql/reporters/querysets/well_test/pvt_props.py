from sqlalchemy import bindparam, func, select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.reflected import (
    DictG,
    HeaderId,
    Reservoir2,
    ResPty,
    WellHdr,
)


def select_pvt_props() -> Select:
    dictg_alias = aliased(DictG)
    reservoir = func.replace(dictg_alias.sdes, "(Руд)")
    return (
        select(
            reservoir.label("reservoir"),
            ResPty.initial_layer_pressure.label("p_init"),
            ResPty.bubble_point_pressure.label("p_bubble"),
        )
        .where(
            HeaderId.uwi == WellHdr.uwi,
            DictG.id == HeaderId.field,
            dictg_alias.sdes == HeaderId.cid,
            DictG.description == bindparam("field"),
            (
                func.regexp_replace(WellHdr.well_name, r"B\d+$")
                == bindparam("well")
            ),
            reservoir.in_(bindparam("reservoirs")),
            ResPty.reservoir_s == Reservoir2.reservoir_s,
            Reservoir2.field_code == HeaderId.field,
            Reservoir2.district == HeaderId.district_id,
            Reservoir2.existence_type == "ACTUAL",
            Reservoir2.reservoir_id == dictg_alias.id,
        )
        .distinct()
    )
