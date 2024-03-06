from datetime import date

import pandas as pd
from dateutil.relativedelta import relativedelta
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

    async def read_all(  # type: ignore[override]
        self,
        *,
        date_from: date,
        date_to: date,
        base_period: int,
        pred_period: int,
    ) -> dict[str, pd.DataFrame]:
        mer_date_from = date_from - relativedelta(months=base_period)
        mer_date_to = date_to + relativedelta(months=pred_period - 1)
        return await super().read_all(
            date_from=date_from,
            date_to=date_to,
            mer_date_from=mer_date_from,
            mer_date_to=mer_date_to,
        )
