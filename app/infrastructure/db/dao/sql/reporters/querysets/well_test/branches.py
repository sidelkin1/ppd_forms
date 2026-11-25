"""Ствол скважины, открытый на дату текущего исследования."""

from sqlalchemy import bindparam, func, or_, select
from sqlalchemy.sql.expression import ScalarSelect, Select

from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    WellHdr,
    WellPerforations,
)

from ..isobar.perfs import _select_field_codes


def _select_reservoir_layer_ids() -> Select:
    """layer_id объектов разработки — по образцу isobar/perfs.py.

    ``layer_id`` перфорации может указывать на «ИЖВ»-объект, у которого
    ``mr`` ссылается на базовый. Резолв идёт в строковом домене
    ``decode(mr, NULL, to_char(id), mr)``, поэтому нечисловой ``mr`` не
    приводит к ORA-01722. Табличные алиасы (а не ``aliased``) выбраны,
    чтобы запрос компилировался в unit-тестах до отражения OFM.
    """
    base = DictG.__table__.alias("base_object")
    mapped = DictG.__table__.alias("mapped_object")
    base_ids = select(func.to_char(base.c.id)).where(
        func.replace(base.c.sdes, "(Руд)", "").in_(
            bindparam("cids", expanding=True)
        )
    )
    return select(mapped.c.id).where(
        func.decode(
            mapped.c.mr, None, func.to_char(mapped.c.id), mapped.c.mr
        ).in_(base_ids)
    )


def _select_base_uwi() -> Select:
    """UWI базовой скважины — имени без суффикса ствола.

    Месторождение резолвится как в isobar: в ``well_hdr.field`` лежит
    код, а в результатах ГДИС — название, поэтому фильтр идёт через
    ``DictG.description``.
    """
    return select(WellHdr.uwi).where(
        WellHdr.well_name == bindparam("well"),
        WellHdr.field.in_(_select_field_codes()),
    )


def _select_open_branch_uwi() -> ScalarSelect:
    """UWI ствола с открытой на дату исследования перфорацией.

    Стволы сводятся к базовой скважине через
    ``coalesce(parent_uwi, uwi)``, из нескольких открытых выбирается
    лексикографически максимальный (``123B2`` после ``123B1``). Условие
    открытости задано явно: ``BETWEEN`` отбросил бы интервалы с
    ``close_date IS NULL``.
    """
    base = _select_base_uwi().subquery()
    branch = WellHdr.__table__.alias("perf_branch")
    return (
        select(func.max(branch.c.uwi).label("uwi"))
        .select_from(WellPerforations.__table__)
        .join(branch, branch.c.uwi == WellPerforations.uwi)
        .where(
            func.coalesce(branch.c.parent_uwi, branch.c.uwi) == base.c.uwi,
            WellPerforations.comp_date <= bindparam("end_date"),
            or_(
                WellPerforations.close_date.is_(None),
                WellPerforations.close_date >= bindparam("end_date"),
            ),
            WellPerforations.layer_id.in_(_select_reservoir_layer_ids()),
        )
        .scalar_subquery()
    )


def select_well_branch() -> Select:
    """Имя ствола, открытого на дату исследования.

    Если открытой перфорации нет, возвращается базовая скважина — по
    аналогии с ``owc_resp/branches.py``.
    """
    base = _select_base_uwi().subquery()
    branch = WellHdr.__table__.alias("branch")
    return select(branch.c.well_name.label("branch")).where(
        branch.c.uwi == func.coalesce(_select_open_branch_uwi(), base.c.uwi)
    )
