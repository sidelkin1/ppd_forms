from sqlalchemy import bindparam, case, func, literal, select
from sqlalchemy.sql.expression import (
    ColumnElement,
    ScalarSelect,
    Select,
)

from app.infrastructure.db.models.ofm.udmurtneft_n import WellMonthHist

from .branches import select_well_base_uwi
from .reservoirs import select_reservoir_ids


def _select_mer_where() -> tuple[ColumnElement[bool], ...]:
    """Фильтры МЭР: базовая скважина, выбранный объект и дата отчёта."""
    return (
        WellMonthHist.uwi.in_(select_well_base_uwi()),
        WellMonthHist.layer_id.in_(select_reservoir_ids()),
        WellMonthHist.start_date <= bindparam("on_date"),
    )


def select_mer_date() -> ScalarSelect:
    """Дата последней записи МЭР не позже даты отчёта."""
    return (
        select(func.max(WellMonthHist.start_date))
        .where(*_select_mer_where())
        .scalar_subquery()
    )


def select_mer_rates() -> Select:
    """Дебиты МЭР одной строкой (даже при отсутствии записей).

    Записи выбранной даты агрегируются в одну строку. Месячная добыча
    переводится в суточную множителем 24 (``act_time`` — часы). При
    нулевом времени работы дебиты остаются ``NULL``. Объём жидкости и
    обводненность считаются по ``oil_v + water_v``, если объёмная
    добыча положительна, иначе по массе ``oil + water``; при пустых
    обоих знаменателях обводненность равна 100 %.
    """
    act_time = func.sum(WellMonthHist.act_time)
    volume = func.sum(
        func.coalesce(WellMonthHist.oil_v, 0)
        + func.coalesce(WellMonthHist.water_v, 0)
    )
    mass = func.sum(
        func.coalesce(WellMonthHist.oil, 0)
        + func.coalesce(WellMonthHist.water, 0)
    )
    amount = case((volume > 0, volume), else_=mass)
    return select(
        func.max(WellMonthHist.start_date).label("date"),
        case(
            (act_time > 0, 24 * func.sum(WellMonthHist.oil) / act_time)
        ).label("oil_rate"),
        case((act_time > 0, 24 * amount / act_time)).label("liq_rate"),
        case(
            (
                volume > 0,
                func.sum(func.coalesce(WellMonthHist.water_v, 0))
                / volume
                * 100,
            ),
            (
                mass > 0,
                func.sum(func.coalesce(WellMonthHist.water, 0)) / mass * 100,
            ),
            else_=literal(100),
        ).label("watercut"),
    ).where(
        *_select_mer_where(),
        WellMonthHist.start_date == select_mer_date(),
    )
