from sqlalchemy import bindparam, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.local import NewStrategyOil


def select_new_strategy_oil() -> Select:
    return select(
        NewStrategyOil.field,
        NewStrategyOil.well,
        NewStrategyOil.gtm_name,
        NewStrategyOil.vnr_date,
    ).where(
        NewStrategyOil.start_date <= bindparam("date_to"),
        NewStrategyOil.vnr_date >= bindparam("date_from"),
    )
