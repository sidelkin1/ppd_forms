import asyncio
from dataclasses import dataclass
from datetime import date
from typing import cast

import pandas as pd
from dateutil.relativedelta import relativedelta

from app.core.models.dto import WellTestResult
from app.infrastructure.db.dao.sql import reporters as db
from app.infrastructure.db.dao.sql.reporters.ofm_well_test import PERF_COLUMNS
from app.infrastructure.files.dao import reporters as files


def _history_start(tests: pd.DataFrame) -> date | None:
    """Дата самого раннего предыдущего ГДИС.

    Перфорации нужны с этого момента: интервалы, закрытые раньше, на
    даты истории уже не открыты. Для пустой истории запрос в OFM не
    выполняется.
    """
    if tests.empty or "end_date" not in tests.columns:
        return None
    dates = pd.to_datetime(tests["end_date"], errors="coerce").dropna()
    if dates.empty:
        return None
    return dates.min().date()


@dataclass
class WellTestReporter:
    history: db.LocalWellTestReporter
    results: files.WellTestReporter
    ofm: db.OfmWellTestReporter

    async def get_results(self) -> list[WellTestResult]:
        results = await self.results.get_results()
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(self._get_branch(result)) for result in results
            ]
        return [
            cast(WellTestResult, {**result, "branch": task.result()})
            for result, task in zip(results, tasks)
        ]

    async def _get_branch(self, result: WellTestResult) -> str:
        """Ствол с открытой на дату исследования перфорацией.

        Запрос выполняется для каждой пары «месторождение, скважина,
        объект, дата»: у одного исследования может быть несколько
        объектов. Если ствол не найден, остаётся базовая скважина.
        """
        branches = await self.ofm.read_one(
            key="branches",
            fields=[result["field"]],
            well=result["well"],
            cids=[result["reservoir"]],
            end_date=result["end_date"],
        )
        if branches.empty:
            return result["well"]
        return str(branches["branch"].iat[0])

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

    async def get_perfs(
        self,
        *,
        field: str,
        well: str,
        reservoirs: list[str],
        tests: pd.DataFrame,
    ) -> pd.DataFrame:
        """Интервалы перфорации стволов на даты предыдущих ГДИС.

        ``history_start`` — дата самого раннего предыдущего исследования:
        интервалы, закрытые раньше, на даты истории уже не открыты.
        """
        history_start = _history_start(tests)
        if history_start is None:
            return pd.DataFrame(columns=list(PERF_COLUMNS))
        return await self.ofm.read_one(
            key="perfs",
            fields=[field],
            wells=[well],
            cids=reservoirs,
            history_start=history_start,
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
        tests = tests_task.result()
        perfs = await self.get_perfs(
            field=results[0]["field"],
            well=results[0]["well"],
            reservoirs=reservoirs,
            tests=tests,
        )
        neighb_tests = await self.get_neighb_tests(
            neighbs["field"].to_list(),
            neighbs["well"].to_list(),
            neighbs["reservoir"].to_list(),
            results[0]["end_date"],
            gdis_period,
        )
        return {
            "gtms": gtms_task.result(),
            "tests": tests,
            "perfs": perfs,
            "neighbs": neighbs,
            "neighb_tests": neighb_tests,
            "pvt": pvt_task.result(),
        }
