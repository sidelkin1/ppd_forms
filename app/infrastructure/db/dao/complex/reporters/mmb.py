from dataclasses import dataclass

import pandas as pd

from app.infrastructure.db.dao.sql import reporters as db
from app.infrastructure.files.dao import reporters as files


@dataclass
class MmbReporter:
    hist: db.MmbReporter
    hist_alt: db.MmbAltReporter
    description: files.MmbReporter

    async def get_history(
        self, uids: list[str], alternative: bool
    ) -> dict[str, pd.DataFrame]:
        if alternative:
            return await self.hist_alt.read_all(uids=uids)
        return await self.hist.read_all(uids=uids)

    async def get_description(self) -> pd.DataFrame:
        return await self.description.get_description()
