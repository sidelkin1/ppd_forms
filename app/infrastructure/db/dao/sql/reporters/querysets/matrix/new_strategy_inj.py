from sqlalchemy import bindparam, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.local import NewStrategyInj


def select_new_strategy_inj() -> Select:
    return select(
        NewStrategyInj.field,
        NewStrategyInj.well,
        NewStrategyInj.reservoir,
        NewStrategyInj.gtm_date,
        NewStrategyInj.gtm_description,
        NewStrategyInj.gtm_group,
        NewStrategyInj.gtm_problem,
        NewStrategyInj.reservoir_neighbs,
        NewStrategyInj.neighbs,
    ).where(
        NewStrategyInj.gtm_date >= bindparam("date_from"),
        NewStrategyInj.gtm_date <= bindparam("date_to"),
    )
