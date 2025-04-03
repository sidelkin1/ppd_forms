import asyncio
from dataclasses import dataclass
from datetime import date

import pandas as pd
from dateutil.relativedelta import relativedelta

from app.core.models.dto import WellTestResult
from app.infrastructure.db.dao.sql import reporters as db
from app.infrastructure.files.dao import reporters as files


@dataclass
class WellTestReporter:
    history: db.LocalWellTestReporter
    results: files.WellTestReporter
    ofm: db.OfmWellTestReporter

    async def get_results(self) -> list[WellTestResult]:
        return await self.results.get_results()

    async def get_well_gtms(
        self, field: str, well: str, end_date: date, gtm_period: int
    ) -> pd.DataFrame:
        date_from = end_date.replace(day=1) - relativedelta(months=gtm_period)
        return await self.history.read_one(
            key="gtm",
            field=field,
            well=well,
            date_from=date_from,
            date_to=end_date,
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
        return await self.ofm.read_one(
            key="neighbs",
            field=field,
            well=well,
            reservoirs=reservoirs,
            radius=radius,
        )

    async def get_neighb_tests(
        self,
        fields: list[str],
        wells: list[str],
        reservoirs: list[str],
        end_date: date,
        gdis_period: int,
    ) -> pd.DataFrame:
        uids = list(map("".join, zip(fields, wells, reservoirs)))
        date_from = end_date.replace(day=1) - relativedelta(years=gdis_period)
        return await self.history.read_one(
            key="neighbs",
            uids=uids,
            date_from=date_from,
            report_date=end_date,
        )

    async def get_pvt(
        self, field: str, well: str, reservoirs: list[str]
    ) -> pd.DataFrame:
        return await self.ofm.read_one(
            key="pvt",
            field=field,
            well=well,
            reservoirs=reservoirs,
        )

    async def read_all(
        self,
        *,
        results: list[WellTestResult],
        gtm_period: int,
        gdis_period: int,
        radius: float,
    ) -> dict[str, pd.DataFrame]:
        reservoirs = [result["reservoir"] for result in results]
        async with asyncio.TaskGroup() as tg:
            gtms_task = tg.create_task(
                self.get_well_gtms(
                    results[0]["field"],
                    results[0]["well"],
                    results[0]["end_date"],
                    gtm_period,
                )
            )
            tests_task = tg.create_task(
                self.get_well_tests(
                    results[0]["field"],
                    results[0]["well"],
                    reservoirs,
                    results[0]["end_date"],
                )
            )
            neighbs_task = tg.create_task(
                self.get_neighbs(
                    results[0]["field"],
                    results[0]["well"],
                    reservoirs,
                    radius,
                )
            )
            pvt_task = tg.create_task(
                self.get_pvt(
                    results[0]["field"], results[0]["well"], reservoirs
                )
            )
        neighbs = neighbs_task.result()
        neighb_tests = await self.get_neighb_tests(
            neighbs["field"].to_list(),
            neighbs["well"].to_list(),
            neighbs["reservoir"].to_list(),
            results[0]["end_date"],
            gdis_period,
        )
        return {
            "gtms": gtms_task.result(),
            "tests": tests_task.result(),
            "neighbs": neighbs,
            "neighb_tests": neighb_tests,
            "pvt": pvt_task.result(),
        }
