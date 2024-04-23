from sqlalchemy import bindparam, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.reflected import (
    DictG,
    MonthlyInj,
    MonthlyProd,
)


def select_fields() -> Select:
    return (
        select(DictG.id, DictG.description.label("name"))
        .where(DictG.grp == 1670, DictG.code.is_not(None))
        .order_by("name")
    )


def select_field() -> Select:
    return select_fields().where(DictG.id == bindparam("field_id"))


def select_production_fields() -> Select:
    return (
        select(
            MonthlyProd.field.label("id"),
            DictG.description.label("name"),
        )
        .join(DictG, MonthlyProd.field == DictG.id)
        .distinct()
        .order_by("name")
    )


def select_production_field() -> Select:
    return select_production_fields().where(
        MonthlyProd.field == bindparam("field_id")
    )


def select_injection_fields() -> Select:
    return (
        select(
            MonthlyInj.field.label("id"),
            DictG.description.label("name"),
        )
        .join(DictG, MonthlyInj.field == DictG.id)
        .distinct()
        .order_by("name")
    )


def select_injection_field() -> Select:
    return select_injection_fields().where(
        MonthlyInj.field == bindparam("field_id")
    )
