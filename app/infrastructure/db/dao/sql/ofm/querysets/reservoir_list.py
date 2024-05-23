from sqlalchemy import bindparam, func, select, union
from sqlalchemy.sql.expression import (
    ColumnElement,
    CompoundSelect,
    ScalarSelect,
    Select,
)

from app.infrastructure.db.models.ofm.reflected import DictG, WellStockHistExt


def _select_field_code() -> ScalarSelect:
    return (
        select(DictG.code.label("id"))
        .where(DictG.id == bindparam("field_id"))
        .scalar_subquery()
    )


def _select_reservoir_id(ora: ColumnElement) -> Select:
    return (
        select(ora.label("id"))
        .where(
            WellStockHistExt.uwi.like(func.concat(_select_field_code(), "%")),
            ora.is_not(None),
        )
        .distinct()
    )


def _select_reservoir_ids() -> CompoundSelect:
    return union(
        _select_reservoir_id(WellStockHistExt.ora1),
        _select_reservoir_id(WellStockHistExt.ora2),
        _select_reservoir_id(WellStockHistExt.ora3),
    )


def select_reservoirs() -> Select:
    return (
        select(
            func.decode(DictG.mr, None, DictG.id, DictG.mr).label("id"),
            func.udmurtneft_n.dg_sdes(
                func.decode(DictG.mr, None, DictG.id, DictG.mr)
            ).label("name"),
        )
        .where(DictG.id.in_(_select_reservoir_ids()))
        .distinct()
        .order_by("name")
    )
