from sqlalchemy import (
    bindparam,
    func,
    literal,
    null,
    select,
    union_all,
)
from sqlalchemy.sql.expression import Select
from sqlalchemy.sql.selectable import Subquery

from app.infrastructure.db.models.ofm.udmurtneft_n import (
    TmpWellNgOis2,
    TmpWellOpOis2,
)

from .branches import select_well_base_uwi
from .reservoirs import select_reservoir_names


def _select_tr_rows() -> Subquery:
    """Техрежимы нефтяного и нагнетательного фонда одной выборкой.

    Техрежим хранит базовый UWI без суффикса ствола, а объект — текстом,
    поэтому фильтр по UWI идёт через родительскую скважину, а по пласту —
    через ``select_reservoir_names()``. Ветка нагнетательного фонда
    дополняется столбцами нефтяного: нефти нет, обводненность 100 %,
    дебит жидкости — приемистость.
    """
    oil = select(
        TmpWellOpOis2.official_date.label("official_date"),
        TmpWellOpOis2.layer_id.label("layer_id"),
        TmpWellOpOis2.oil_rate.label("oil_rate"),
        TmpWellOpOis2.liq_rate.label("liq_rate"),
        TmpWellOpOis2.water_cut.label("watercut"),
        TmpWellOpOis2.flow_pressure.label("bhp"),
        literal(0).label("src"),
    ).where(
        TmpWellOpOis2.uwi.in_(select_well_base_uwi()),
        TmpWellOpOis2.official_date <= bindparam("on_date"),
        func.lower(TmpWellOpOis2.layer_id).in_(select_reservoir_names()),
    )
    inj = select(
        TmpWellNgOis2.official_date.label("official_date"),
        TmpWellNgOis2.layer_id.label("layer_id"),
        null().label("oil_rate"),
        TmpWellNgOis2.intake.label("liq_rate"),
        literal(100).label("watercut"),
        TmpWellNgOis2.layer_flow_pressure.label("bhp"),
        literal(1).label("src"),
    ).where(
        TmpWellNgOis2.uwi.in_(select_well_base_uwi()),
        TmpWellNgOis2.official_date <= bindparam("on_date"),
        func.lower(TmpWellNgOis2.layer_id).in_(select_reservoir_names()),
    )
    return union_all(oil, inj).subquery("tr_rows")


def _select_tr_ranked() -> Subquery:
    """Строки ТР с номером: последняя дата, при равенстве — нефтяной фонд.

    Дубликаты по дате и фонду (например, несколько пластов) сводятся
    к одной строке детерминированным порядком по ``layer_id``.
    """
    rows = _select_tr_rows()
    return select(
        rows.c.official_date,
        rows.c.oil_rate,
        rows.c.liq_rate,
        rows.c.watercut,
        rows.c.bhp,
        func.row_number()
        .over(
            order_by=(
                rows.c.official_date.desc(),
                rows.c.src,
                rows.c.layer_id,
            )
        )
        .label("rn"),
    ).subquery("tr_ranked")


def select_tr_rates() -> Select:
    """Дебиты и забойное давление последнего ТР одной строкой."""
    ranked = _select_tr_ranked()
    return select(
        ranked.c.official_date.label("date"),
        ranked.c.oil_rate,
        ranked.c.liq_rate,
        ranked.c.watercut,
        ranked.c.bhp.label("tr_bhp"),
    ).where(ranked.c.rn == 1)
