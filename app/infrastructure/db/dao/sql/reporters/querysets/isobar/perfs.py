from sqlalchemy import bindparam, func, select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    WellHdr,
    WellPerforations,
)

from .common import cid_column


def _select_reservoir_layer_ids() -> Select:
    """layer_id объектов разработки, к которым относится запрос (cid).

    ``layer_id`` перфорации может указывать на «ИЖВ»-объект, у которого
    ``mr`` — ссылка на базовый объект. Резолв идёт через
    ``decode(mr, NULL, to_char(id), mr)``: всё в строковом домене, поэтому
    никаких ORA-01722 (``dg_sdes`` в WHERE падал на нечисловых ``mr``).
    """
    base = aliased(DictG)
    mapped = aliased(DictG)
    base_ids = select(func.to_char(base.id)).where(
        func.replace(base.sdes, "(Руд)", "").in_(
            bindparam("cids", expanding=True)
        )
    )
    return select(mapped.id).where(
        func.decode(mapped.mr, None, func.to_char(mapped.id), mapped.mr).in_(
            base_ids
        )
    )


def _select_field_codes() -> Select:
    """Коды месторождений по их названиям из справочника.

    В ``well_hdr.field`` лежит код, а в замерах — название, поэтому фильтр
    по полю идёт через справочник: ``description`` → ``to_char(id)``.
    """
    return select(func.to_char(DictG.id)).where(
        DictG.description.in_(bindparam("fields", expanding=True))
    )


def select_well_perfs() -> Select:
    """Интервалы перфорации стволов по скважинам и объектам квартала.

    ``fields`` — названия месторождений, ``wells`` — имена скважин без
    ствола, ``cids`` — объекты разработки (тот же домен, что ``cid``
    фонда), ``previous_date`` — начало квартала: интервалы, закрытые
    раньше, на дату замера уже не открыты.

    В WHERE только «дешёвые» условия: имена и коды, даты и резолв
    ``layer_id`` подзапросом по справочнику. ``dg_sdes`` считается в
    выборке — уже после фильтрации.
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
        # скважина без ствола: родитель ствола либо сам ствол
        .join(base, base.uwi == func.coalesce(branch.parent_uwi, branch.uwi))
        .join(DictG, DictG.id == WellPerforations.layer_id)
        .where(
            branch.field.in_(_select_field_codes()),
            base.well_name.in_(bindparam("wells", expanding=True)),
            WellPerforations.layer_id.in_(_select_reservoir_layer_ids()),
            WellPerforations.close_date.is_(None)
            | (WellPerforations.close_date >= bindparam("previous_date")),
        )
        .distinct()
    )
