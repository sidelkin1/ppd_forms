from sqlalchemy import bindparam, func, or_, select
from sqlalchemy.sql.expression import ColumnElement, ScalarSelect

from app.infrastructure.db.models.ofm.udmurtneft_n import (
    WellHdr,
    WellPerforations,
)

from .reservoirs import select_reservoir_ids


def _perf_where() -> tuple[ColumnElement[bool], ...]:
    """Общие фильтры перфорации: ствол, пласт и активность на дату.

    Открытый интервал хранится с ``close_date IS NULL``, поэтому активность
    проверяется как ``comp_date <= on_date AND (close_date IS NULL OR
    close_date >= on_date)`` — ``BETWEEN`` здесь отбросил бы открытые
    интервалы.
    """
    return (
        WellPerforations.uwi == WellHdr.uwi,
        WellPerforations.layer_id.in_(select_reservoir_ids()),
        WellPerforations.comp_date <= bindparam("on_date"),
        or_(
            WellPerforations.close_date.is_(None),
            WellPerforations.close_date >= bindparam("on_date"),
        ),
    )


def select_top_perf() -> ScalarSelect:
    """Верхняя перфорация (минимальная глубина)."""
    return (
        select(func.min(WellPerforations.top))
        .where(*_perf_where())
        .scalar_subquery()
        .correlate(WellHdr.__table__)
    )


def select_bottom_perf() -> ScalarSelect:
    """Нижняя перфорация (максимальная глубина)."""
    return (
        select(func.max(WellPerforations.base))
        .where(*_perf_where())
        .scalar_subquery()
        .correlate(WellHdr.__table__)
    )
