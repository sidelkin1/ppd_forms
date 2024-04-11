from sqlalchemy import func, select
from sqlalchemy.sql.expression import Select, Subquery

from app.infrastructure.db.models.local import NewStrategyInj


def _select_last_gtm() -> Subquery:
    return (
        select(
            NewStrategyInj.field,
            NewStrategyInj.well,
            func.max(NewStrategyInj.gtm_date).label("max_date"),
        )
        .where(NewStrategyInj.neighbs.is_not(None))
        .group_by(
            NewStrategyInj.field,
            NewStrategyInj.well,
        )
        .subquery()
    )


def select_new_strategy_inj() -> Select:
    last_gtm = _select_last_gtm()
    return select(
        NewStrategyInj.field,
        NewStrategyInj.well,
        NewStrategyInj.reservoir,
        NewStrategyInj.gtm_date,
        NewStrategyInj.gtm_group,
        NewStrategyInj.reservoir_neighbs,
        NewStrategyInj.neighbs,
    ).where(
        NewStrategyInj.field == last_gtm.c.field,
        NewStrategyInj.well == last_gtm.c.well,
        NewStrategyInj.gtm_date == last_gtm.c.max_date,
    )
