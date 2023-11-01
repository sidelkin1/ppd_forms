from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.dao.complex.reporter.base import BaseDAO
from app.infrastructure.db.dao.complex.reporter.querysets.oil_loss import (
    select_inj_well_database,
    select_monthly_report,
    select_neighborhood,
    select_new_strategy_inj,
)


class OilLossReporter(BaseDAO):
    def __init__(self, pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(
            {
                "inj_db": select_inj_well_database(),
                "neighbs": select_neighborhood(),
                "ns_ppd": select_new_strategy_inj(),
                "mer": select_monthly_report(),
            },
            pool,
        )
