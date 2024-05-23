from sqlalchemy import bindparam, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.reflected import (
    DictG,
    MonthlyInj,
    MonthlyProd,
)


def select_fields(with_field_id: bool = False) -> Select:
    stmt = (
        select(DictG.id, DictG.description.label("name"))
        .where(DictG.grp == 1670, DictG.code.is_not(None))
        .order_by("name")
    )
    return (
        stmt.where(DictG.id == bindparam("field_id"))
        if with_field_id
        else stmt
    )


def select_production_fields(with_field_id: bool = False) -> Select:
    stmt = (
        select(
            MonthlyProd.field.label("id"),
            DictG.description.label("name"),
        )
        .join(DictG, MonthlyProd.field == DictG.id)
        .distinct()
        .order_by("name")
    )
    return (
        stmt.where(MonthlyProd.field == bindparam("field_id"))
        if with_field_id
        else stmt
    )


def select_injection_fields(with_field_id: bool = False) -> Select:
    stmt = (
        select(
            MonthlyInj.field.label("id"),
            DictG.description.label("name"),
        )
        .join(DictG, MonthlyInj.field == DictG.id)
        .distinct()
        .order_by("name")
    )
    return (
        stmt.where(MonthlyInj.field == bindparam("field_id"))
        if with_field_id
        else stmt
    )
