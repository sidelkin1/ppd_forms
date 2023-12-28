from functools import reduce

from sqlalchemy import func, select
from sqlalchemy.sql.expression import ScalarSelect

from app.infrastructure.db.models.ofm.base import Base
from app.infrastructure.db.models.ofm.reflected import (
    DictG,
    WellHdr,
    WellStockHistExt,
)

MAX_NUMBER_OF_ORA = 3


def select_description(
    model: type[Base], field_id: str, field_descr: str = "description"
) -> ScalarSelect:
    return (
        select(getattr(DictG, field_descr))
        .where(getattr(model, field_id) == DictG.id)
        .scalar_subquery()
        .correlate(model)
    )


def select_reservoir(model: type[Base], field_id: str) -> ScalarSelect:
    return (
        select(
            func.udmurtneft_n.dg_sdes(
                func.decode(DictG.mr, None, DictG.id, DictG.mr)
            )
        )
        .where(getattr(model, field_id) == DictG.id)
        .scalar_subquery()
        .correlate(model)
    )


def select_well_name(model: type[Base], field_id: str) -> ScalarSelect:
    return (
        select(WellHdr.well_name)
        .where(getattr(model, field_id) == WellHdr.uwi)
        .scalar_subquery()
        .correlate(model)
    )


def select_cids() -> ScalarSelect:
    subqs = (
        select_reservoir(WellStockHistExt, f"ora{num}")
        for num in range(1, MAX_NUMBER_OF_ORA + 1)
    )
    # sourcery skip: use-fstring-for-concatenation
    return reduce(
        lambda result, subq: func.decode(
            subq,
            None,
            result,
            subq + " " + result,
        ),
        subqs,
    )
