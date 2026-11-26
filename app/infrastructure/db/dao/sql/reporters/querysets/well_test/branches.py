"""Ствол скважины, открытый на дату текущего исследования."""

from sqlalchemy import bindparam, func, or_, select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import ScalarSelect, Select

from app.infrastructure.db.models.ofm.udmurtneft_n import (
    WellHdr,
    WellPerforations,
)

from .common import select_field_codes, select_reservoir_layer_ids


def _select_base_uwi() -> Select:
    """UWI базовой скважины по имени без суффикса ствола."""
    return select(WellHdr.uwi).where(
        WellHdr.well_name == bindparam("well"),
        WellHdr.field.in_(select_field_codes()),
    )


def _select_open_branch_uwi() -> ScalarSelect:
    """UWI ствола с открытой на дату исследования перфорацией."""
    base = _select_base_uwi().subquery()
    branch = aliased(WellHdr)
    return (
        select(func.max(branch.uwi).label("uwi"))
        .select_from(WellPerforations)
        .join(branch, branch.uwi == WellPerforations.uwi)
        .where(
            func.coalesce(branch.parent_uwi, branch.uwi) == base.c.uwi,
            WellPerforations.comp_date <= bindparam("end_date"),
            or_(
                WellPerforations.close_date.is_(None),
                WellPerforations.close_date >= bindparam("end_date"),
            ),
            WellPerforations.layer_id.in_(select_reservoir_layer_ids()),
        )
        .scalar_subquery()
    )


def select_well_branch() -> Select:
    """Имя ствола, открытого на дату исследования."""
    base = _select_base_uwi().subquery()
    branch = aliased(WellHdr)
    return select(branch.well_name.label("branch")).where(
        branch.uwi == func.coalesce(_select_open_branch_uwi(), base.c.uwi)
    )
