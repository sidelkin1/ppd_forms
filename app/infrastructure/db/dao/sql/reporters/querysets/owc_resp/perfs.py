from sqlalchemy import between, bindparam, func, select
from sqlalchemy.sql.expression import ColumnElement, ScalarSelect

from app.infrastructure.db.models.ofm.udmurtneft_n import (
    WellHdr,
    WellPerforations,
)

from .reservoirs import select_reservoir_ids


def _perf_where() -> tuple[ColumnElement[bool], ...]:
    """Общие фильтры перфорации: ствол, пласт и активность на дату."""
    return (
        WellPerforations.uwi == WellHdr.uwi,
        WellPerforations.layer_id.in_(select_reservoir_ids()),
        between(
            bindparam("on_date"),
            WellPerforations.comp_date,
            WellPerforations.close_date,
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
