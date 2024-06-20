from dataclasses import dataclass

import pandas as pd

from app.infrastructure.db.dao.sql import reporters as db
from app.infrastructure.files.dao import reporters as files


@dataclass
class MmbReporter:
    history: db.MmbReporter
    description: files.MmbReporter

    async def get_history(
        self,
        fields: list[str],
        wells: list[str],
        reservoirs: list[str],
        alternative: bool,
    ) -> pd.DataFrame:
        return await self.history.get_history(
            fields, reservoirs, wells, alternative
        )

    async def get_description(self) -> pd.DataFrame:
        return await self.description.get_description()
