from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.dao.sql.reporters.local import LocalBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import inj_loss


class FirstRateInjLossReporter(LocalBaseDAO):
    def __init__(self, pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(
            {
                "inj_db": inj_loss.select_inj_well_database(),
                "neighbs": inj_loss.select_neighborhood(),
                "ns_ppd": inj_loss.select_new_strategy_inj(),
                "ns_oil": inj_loss.select_new_strategy_oil(),
                "mer": inj_loss.select_monthly_report_for_first_rate(),
            },
            pool,
        )


class MaxRateInjLossReporter(LocalBaseDAO):
    def __init__(self, pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(
            {
                "inj_db": inj_loss.select_inj_well_database(),
                "neighbs": inj_loss.select_neighborhood(),
                "ns_ppd": inj_loss.select_new_strategy_inj(),
                "ns_oil": inj_loss.select_new_strategy_oil(),
                "mer": inj_loss.select_monthly_report_for_max_rate(),
            },
            pool,
        )
