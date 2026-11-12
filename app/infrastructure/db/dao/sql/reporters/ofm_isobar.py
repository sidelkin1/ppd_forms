import asyncio
from collections.abc import Sequence
from datetime import date

import pandas as pd
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import isobar

PERF_COLUMNS = (
    "field",
    "well",
    "reservoir",
    "branch",
    "comp_date",
    "close_date",
)
_GROUP_SIZE = 900  # лимит списка IN в Oracle — 1000 выражений


def _groups(
    keys: Sequence[tuple[str, str, str]],
) -> list[list[tuple[str, str, str]]]:
    return [
        list(keys[start : start + _GROUP_SIZE])
        for start in range(0, len(keys), _GROUP_SIZE)
    ]


class OfmIsobarReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "stock": isobar.select_stock(),
                "perfs": isobar.select_well_perfs(),
            },
            pool,
        )

    async def read_perfs(
        self,
        rows: Sequence[tuple[str, str, str]],
        previous_date: date,
    ) -> pd.DataFrame:
        """Интервалы перфорации стволов по ключам текущих замеров.

        ``rows`` — уникальные тройки (месторождение, скважина без ствола,
        объект). Ключи режутся на группы под лимит ``IN`` в Oracle; групп
        получается 1–2, поэтому запросы идут параллельно.
        """
        keys = sorted(set(rows))
        if not keys:
            return pd.DataFrame(columns=list(PERF_COLUMNS))
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(
                    self.read_one(
                        key="perfs",
                        fields=sorted({key[0] for key in group}),
                        wells=sorted({key[1] for key in group}),
                        cids=sorted({key[2] for key in group}),
                        previous_date=previous_date,
                    )
                )
                for group in _groups(keys)
            ]
        return pd.concat([task.result() for task in tasks], ignore_index=True)
