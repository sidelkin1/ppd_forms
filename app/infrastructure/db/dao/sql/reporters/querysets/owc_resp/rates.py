from sqlalchemy import and_, case, or_, select, true
from sqlalchemy.sql.expression import Select

from .mer_rates import select_mer_rates
from .tr_rates import select_tr_rates


def select_rates() -> Select:
    """Текущие дебиты, обводненность и забойное давление одной строкой.

    Источник — более поздняя запись ТР или МЭР; при равных датах
    приоритет у ТР. Если данных нет ни в одном источнике, все значения
    остаются ``NULL`` (а не 100 % обводненности от пустой МЭР).
    ``tr_bhp`` берётся только из ТР.
    """
    mer = select_mer_rates().subquery("mer_rates")
    tr = select_tr_rates().subquery("tr_rates")
    use_tr = and_(
        tr.c.date.is_not(None),
        or_(mer.c.date.is_(None), tr.c.date >= mer.c.date),
    )
    use_mer = and_(
        mer.c.date.is_not(None),
        or_(tr.c.date.is_(None), mer.c.date > tr.c.date),
    )
    return select(
        case((use_tr, tr.c.oil_rate), (use_mer, mer.c.oil_rate)).label(
            "oil_rate"
        ),
        case((use_tr, tr.c.liq_rate), (use_mer, mer.c.liq_rate)).label(
            "liq_rate"
        ),
        case((use_tr, tr.c.watercut), (use_mer, mer.c.watercut)).label(
            "watercut"
        ),
        tr.c.tr_bhp.label("tr_bhp"),
    ).select_from(mer.outerjoin(tr, true()))
