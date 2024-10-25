from dataclasses import dataclass
from datetime import date

import pandas as pd

from app.core.models.dto import WellTestResult
from app.infrastructure.db.dao.sql import reporters as db
from app.infrastructure.files.dao import reporters as files


@dataclass
class WellTestReporter:
    history: db.LocalWellTestReporter
    results: files.WellTestReporter
    neighbs: db.OfmWellTestReporter

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

    async def get_neighbs(
        self, field: str, well: str, reservoirs: list[str], radius: float
    ) -> pd.DataFrame:
        return await self.neighbs.read_one(
            key="neighbs",
            field=field,
            well=well,
            reservoirs=reservoirs,
            radius=radius,
        )

    async def get_neighb_tests(
        self, uids: list[str], date_from: date, report_date: date
    ) -> pd.DataFrame:
        return await self.history.read_one(
            key="neighbs",
            uids=uids,
            date_from=date_from,
            report_date=report_date,
        )
