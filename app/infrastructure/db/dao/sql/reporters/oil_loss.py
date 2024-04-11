from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.dao.sql.reporters.local import LocalBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import oil_loss


class FirstRateOilLossReporter(LocalBaseDAO):
    def __init__(self, pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(
            {"mer": oil_loss.select_monthly_report_for_first_rate()}, pool
        )


class MaxRateOilLossReporter(LocalBaseDAO):
    def __init__(self, pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(
            {"mer": oil_loss.select_monthly_report_for_max_rate()}, pool
        )
