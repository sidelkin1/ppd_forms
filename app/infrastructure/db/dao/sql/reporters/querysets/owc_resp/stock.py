from sqlalchemy import bindparam, func, select
from sqlalchemy.sql.expression import Subquery

from app.infrastructure.db.models.ofm.reflected import WellStockHist


def _select_max_stock_date() -> Subquery:
    return (
        select(
            WellStockHist.uwi,
            func.max(WellStockHist.status_date).label("max_date"),
        )
        .where(
            WellStockHist.status_date <= bindparam("on_date"),
        )
        .group_by(WellStockHist.uwi)
        .subquery()
    )


def select_well_stock_hist() -> Subquery:
    subq = _select_max_stock_date()
    return (
        select(
            WellStockHist.uwi,
            WellStockHist.prod_class,
            WellStockHist.prod_method,
            WellStockHist.status,
        )
        .where(
            WellStockHist.uwi == subq.c.uwi,
            WellStockHist.status_date == subq.c.max_date,
        )
        .subquery()
    )
