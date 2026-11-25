"""Интервалы перфорации стволов по скважинам и объектам истории ГДИС."""

from sqlalchemy import bindparam, func, or_, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    WellHdr,
    WellPerforations,
)

from ..isobar.common import cid_column
from ..isobar.perfs import _select_field_codes
from .branches import _select_reservoir_layer_ids


def select_well_perfs() -> Select:
    """Интервалы перфорации стволов по скважинам и объектам истории.

    ``fields`` — названия месторождений, ``wells`` — имена скважин без
    ствола, ``cids`` — объекты разработки (тот же домен, что ``cid``
    фонда), ``history_start`` — дата самого раннего предыдущего ГДИС:
    интервалы, закрытые раньше, на даты истории уже не открыты.

    Стволы сводятся к базовой скважине через
    ``coalesce(parent_uwi, uwi)``. В WHERE только «дешёвые» условия:
    имена и коды месторождений, ``layer_id`` и даты; ``dg_sdes``
    считается в выборке — уже после фильтрации. Открытые интервалы
    (``close_date IS NULL``) сохраняются явным условием, потому что
    ``BETWEEN`` их отбросил бы.

    Табличные алиасы (а не ``aliased``) выбраны, чтобы запрос
    компилировался в unit-тестах до отражения OFM.
    """
    branch = WellHdr.__table__.alias("perf_branch")
    base = WellHdr.__table__.alias("perf_base")
    return (
        select(
            func.udmurtneft_n.dg_des(branch.c.field).label("field"),
            base.c.well_name.label("well"),
            cid_column().label("reservoir"),
            branch.c.well_name.label("branch"),
            WellPerforations.comp_date.label("comp_date"),
            WellPerforations.close_date.label("close_date"),
        )
        .select_from(WellPerforations.__table__)
        .join(branch, branch.c.uwi == WellPerforations.uwi)
        # скважина без ствола: родитель ствола либо сам ствол
        .join(
            base,
            base.c.uwi == func.coalesce(branch.c.parent_uwi, branch.c.uwi),
        )
        .join(
            DictG.__table__,
            DictG.__table__.c.id == WellPerforations.layer_id,
        )
        .where(
            branch.c.field.in_(_select_field_codes()),
            base.c.well_name.in_(bindparam("wells", expanding=True)),
            WellPerforations.layer_id.in_(_select_reservoir_layer_ids()),
            or_(
                WellPerforations.close_date.is_(None),
                WellPerforations.close_date >= bindparam("history_start"),
            ),
        )
        .distinct()
    )
