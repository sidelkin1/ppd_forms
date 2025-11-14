from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.dao.sql.reporters.local import LocalBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import matrix


class MatrixReporter(LocalBaseDAO):
    def __init__(self, pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(
            {
                "ns_ppd": matrix.select_new_strategy_inj(),
                "ns_oil": matrix.select_new_strategy_oil(),
                "mer": matrix.select_monthly_report(),
            },
            pool,
        )
