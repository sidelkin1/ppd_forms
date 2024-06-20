import pandas as pd
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import (
    select_tank_alternative_history,
    select_tank_history,
)


class MmbReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "history": select_tank_history(),
                "history_alt": select_tank_alternative_history(),
            },
            pool,
        )

    async def get_history(
        self,
        fields: list[str],
        reservoirs: list[str],
        wells: list[str],
        alternative: bool,
    ) -> pd.DataFrame:
        if alternative:
            return await self.read_one(
                key="history_alt",
                fields=fields,
                reservoirs=reservoirs,
                wells=wells,
            )
        return await self.read_one(
            key="history", fields=fields, reservoirs=reservoirs, wells=wells
        )
