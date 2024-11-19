from dataclasses import dataclass
from datetime import date

import pandas as pd

from app.infrastructure.db.dao.sql import reporters as db
from app.infrastructure.files.dao import reporters as files


@dataclass
class MatrixReporter:
    db_dao: db.MatrixReporter
    file_dao: files.MatrixReporter

    async def read_all(
        self,
        *,
        date_from: date,
        date_to: date,
        base_period: int,
        pred_period: int,
    ) -> dict[str, pd.DataFrame]:
        dfs = await self.db_dao.read_all(
            date_from=date_from,
            date_to=date_to,
            base_period=base_period,
            pred_period=pred_period,
        )
        wells = await self.file_dao.get_wells(
            date_from=date_from, date_to=date_to
        )
        if wells is not None:
            dfs["ns_ppd"] = wells
        return dfs
