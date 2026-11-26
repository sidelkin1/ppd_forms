"""Интервалы перфорации стволов по скважинам и объектам истории ГДИС."""

from sqlalchemy import bindparam, func, or_, select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    WellHdr,
    WellPerforations,
)

from .common import (
    cid_column,
    select_field_codes,
    select_reservoir_layer_ids,
)


def select_well_perfs() -> Select:
    """Интервалы перфорации стволов по скважинам и объектам истории.

    ``fields`` — названия месторождений, ``wells`` — имена скважин без
    ствола, ``cids`` — объекты разработки, ``history_start`` — дата
    самого раннего предыдущего ГДИС.
    """
    branch = aliased(WellHdr)
    base = aliased(WellHdr)
    return (
        select(
            func.udmurtneft_n.dg_des(branch.field).label("field"),
            base.well_name.label("well"),
            cid_column().label("reservoir"),
            branch.well_name.label("branch"),
            WellPerforations.comp_date.label("comp_date"),
            WellPerforations.close_date.label("close_date"),
        )
        .select_from(WellPerforations)
        .join(branch, branch.uwi == WellPerforations.uwi)
        .join(
            base,
            base.uwi == func.coalesce(branch.parent_uwi, branch.uwi),
        )
        .join(DictG, DictG.id == WellPerforations.layer_id)
        .where(
            branch.field.in_(select_field_codes()),
            base.well_name.in_(bindparam("wells", expanding=True)),
            WellPerforations.layer_id.in_(select_reservoir_layer_ids()),
            or_(
                WellPerforations.close_date.is_(None),
                WellPerforations.close_date >= bindparam("history_start"),
            ),
        )
        .distinct()
    )
