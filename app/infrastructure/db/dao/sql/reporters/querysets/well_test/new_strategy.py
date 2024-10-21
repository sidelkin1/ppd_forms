from sqlalchemy import bindparam, literal_column, select, union
from sqlalchemy.sql.expression import CompoundSelect, Select

from app.infrastructure.db.models.local import NewStrategyInj, NewStrategyOil


def _select_new_strategy_oil() -> Select:
    return select(
        NewStrategyOil.field,
        NewStrategyOil.well,
        NewStrategyOil.reservoir_after.label("reservoir"),
        literal_column("'НЕФ'").label("well_type"),
        NewStrategyOil.gtm_name,
        literal_column("NULL").label("gtm_description"),
        NewStrategyOil.vnr_date.label("gtm_date"),
    ).where(
        NewStrategyOil.field == bindparam("field"),
        NewStrategyOil.well == bindparam("well"),
        NewStrategyOil.vnr_date <= bindparam("date_to"),
        NewStrategyOil.vnr_date >= bindparam("date_from"),
    )


def _select_new_strategy_inj() -> Select:
    return select(
        NewStrategyInj.field,
        NewStrategyInj.well,
        NewStrategyInj.reservoir,
        literal_column("'НАГ'").label("well_type"),
        NewStrategyInj.gtm_group.label("gtm_name"),
        NewStrategyInj.gtm_description,
        NewStrategyInj.gtm_date,
    ).where(
        NewStrategyInj.field == bindparam("field"),
        NewStrategyInj.well == bindparam("well"),
        NewStrategyInj.gtm_date <= bindparam("date_to"),
        NewStrategyInj.gtm_date >= bindparam("date_from"),
    )


def select_new_strategy() -> CompoundSelect:
    return union(
        _select_new_strategy_oil(), _select_new_strategy_inj()
    ).order_by("gtm_date")
