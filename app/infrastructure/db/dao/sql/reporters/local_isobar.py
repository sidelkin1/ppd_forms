from collections.abc import Sequence
from datetime import date

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.dao.sql.reporters.local import LocalBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import isobar

_PREVIOUS_BATCH_SIZE = 10_000  # 40 000 параметров — ниже лимита PostgreSQL


class LocalIsobarReporter(LocalBaseDAO):
    def __init__(self, pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(
            {
                "succeeded": isobar.select_succeeded_tests(),
                "failed": isobar.select_failed_tests(),
            },
            pool,
        )

    async def read_previous(
        self, rows: Sequence[tuple[str, str, date, str]]
    ) -> pd.DataFrame:
        if not rows:
            # Пустой VALUES невалиден в PostgreSQL
            return pd.DataFrame(columns=list(isobar.PREV_COLUMNS))
        frames = [
            await self._perform_query(
                isobar.select_previous_tests(
                    rows[start : start + _PREVIOUS_BATCH_SIZE]
                )
            )
            for start in range(0, len(rows), _PREVIOUS_BATCH_SIZE)
        ]
        return pd.concat(frames, ignore_index=True)
