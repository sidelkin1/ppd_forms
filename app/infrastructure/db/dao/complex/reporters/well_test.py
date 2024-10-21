from dataclasses import dataclass
from datetime import date

import pandas as pd

from app.core.models.dto import WellTestResult
from app.infrastructure.db.dao.sql import reporters as db
from app.infrastructure.files.dao import reporters as files


@dataclass
class WellTestReporter:
    history: db.WellTestReporter
    results: files.WellTestReporter

    async def get_results(self) -> list[WellTestResult]:
        return await self.results.get_results()

    async def get_well_gtms(
        self, field: str, well: str, date_from: date, date_to: date
    ) -> pd.DataFrame:
        return await self.history.read_one(
            key="gtm",
            field=field,
            well=well,
            date_from=date_from,
            date_to=date_to,
        )

    async def get_well_tests(
        self, field: str, well: str, reservoirs: list[str], report_date: date
    ) -> pd.DataFrame:
        return await self.history.read_one(
            key="gdis",
            field=field,
            well=well,
            reservoirs=reservoirs,
            report_date=report_date,
        )
