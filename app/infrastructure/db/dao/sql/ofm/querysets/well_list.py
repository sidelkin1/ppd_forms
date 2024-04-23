from sqlalchemy import bindparam, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.reflected import (
    MonthlyInj,
    MonthlyProd,
    WellHdr,
)


def select_production_wells() -> Select:
    return (
        select(
            MonthlyProd.uwi,
            WellHdr.well_name.label("name"),
        )
        .where(MonthlyProd.field == bindparam("field_id"))
        .join(WellHdr, WellHdr.uwi == MonthlyProd.uwi)
        .distinct()
        .order_by(MonthlyProd.uwi)
    )


def select_injection_wells() -> Select:
    return (
        select(
            MonthlyInj.uwi,
            WellHdr.well_name.label("name"),
        )
        .where(MonthlyInj.field == bindparam("field_id"))
        .join(WellHdr, WellHdr.uwi == MonthlyInj.uwi)
        .distinct()
        .order_by(MonthlyInj.uwi)
    )
