import asyncio
import tempfile
from dataclasses import dataclass
from datetime import date
from functools import partial
from pathlib import Path
from shutil import make_archive, unpack_archive

import aiofiles
import numpy as np
import pandas as pd
import scipy.interpolate  # type: ignore
from aiocsv import AsyncWriter
from scipy.interpolate._interpolate import _PPolyBase  # type: ignore

from app.core.models.dto import ProlongExpected
from app.core.models.enums import Interpolation
from app.core.services.reports.log.context import LogContext
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.files.config.models.csv import CsvSettings
from app.infrastructure.files.dao.excel import ProlongExpectedDAO


@dataclass(frozen=True)
class ProlongResult:
    field: str
    well: str
    date: date
    method: Interpolation
    oil: np.ndarray
    liq: np.ndarray


@dataclass(frozen=True)
class ProlongError:
    field: str
    well: str
    date: date
    method: Interpolation
    error: Exception


_interpolation_mapper: dict[Interpolation, _PPolyBase] = {
    Interpolation.akima: partial(
        scipy.interpolate.Akima1DInterpolator, method="makima"
    ),
    Interpolation.cubic: scipy.interpolate.CubicSpline,
    Interpolation.pchip: scipy.interpolate.PchipInterpolator,
}


def _read_report(path: Path) -> pd.DataFrame:
    df = pd.read_excel(  # type: ignore[call-overload]
        path,
        sheet_name="Все(1)",
        header=3,
        usecols=[
            "Дата (год)",
            "Дата (месяц)",
            "Дата (день)",
            "Доп. жидкость, т.",
            "Доп. нефть, т.",
        ],
        engine="calamine",
    )
    df.columns = [
        "year",
        "month",
        "day",
        "liq",
        "oil",
    ]  # type: ignore[assignment]
    return df


def _fill_actual(
    garip: pd.DataFrame, report: pd.DataFrame, gtm_date: date
) -> pd.DataFrame:
    cols = ["year", "month", "day"]
    crit = pd.to_datetime(report[cols]) >= pd.to_datetime(
        gtm_date.replace(day=1)
    )
    garip["oil"] = garip["oil"].fillna(
        report.loc[crit, "oil"].reset_index(drop=True)
    )
    garip["liq"] = garip["liq"].fillna(
        report.loc[crit, "liq"].reset_index(drop=True)
    )
    garip.loc[0] = np.nan
    return garip


def _interpolate_garip(
    garip: pd.DataFrame,
    fluid: str,
    total_1: float,
    total_5: float,
    interpolator: _PPolyBase,
) -> pd.DataFrame:
    fluid_total = f"{fluid}_total"
    garip[fluid_total] = garip[fluid].cumsum()
    garip[fluid_total] = garip[fluid_total].fillna(
        {0: 0, 12: total_1 * 1000, 60: total_5 * 1000},
    )
    crit = garip[fluid_total].notna()
    interp = interpolator(garip.index[crit], garip.loc[crit, fluid_total])
    garip[f"{fluid}_garip"] = np.concatenate(
        ([0], np.diff(interp(garip.index))),  # type: ignore
    )
    return garip


def _process_data(
    path: Path, expected: ProlongExpected, interpolation: Interpolation
) -> pd.DataFrame:
    report = _read_report(path / expected.report)
    garip = pd.DataFrame({"oil": np.nan, "liq": np.nan}, index=np.arange(61))
    garip = _fill_actual(garip, report, expected.date)
    interp = _interpolation_mapper[interpolation]
    garip = _interpolate_garip(
        garip, "oil", expected.oil_total_1, expected.oil_total_5, interp
    )
    garip = _interpolate_garip(
        garip, "liq", expected.liq_total_1, expected.liq_total_5, interp
    )
    return garip


async def _process_well(
    path: Path,
    expected: ProlongExpected,
    interpolation: Interpolation,
    results: asyncio.Queue[ProlongResult],
    failures: asyncio.Queue[ProlongError],
    pool: ProcessPoolManager,
) -> None:
    try:
        df = await pool.run(_process_data, path, expected, interpolation)
        await results.put(
            ProlongResult(
                expected.field,
                expected.well,
                expected.date,
                interpolation,
                df["oil_garip"].to_numpy(),
                df["liq_garip"].to_numpy(),
            )
        )
    except Exception as error:
        await failures.put(
            ProlongError(
                expected.field,
                expected.well,
                expected.date,
                interpolation,
                error,
            )
        )


async def _handle_results(
    path: Path,
    encoding: str,
    delimiter: str,
    results: asyncio.Queue[ProlongResult],
    tasks: list[asyncio.Task],
) -> None:
    async with aiofiles.open(
        path / "garip.csv", mode="w", encoding=encoding, newline=""
    ) as afp:
        writer = AsyncWriter(afp, delimiter=delimiter)
        await writer.writerow(
            ["field", "well", "date", "fluid", "method", *range(61)]
        )
        while not (all(task.done() for task in tasks) and results.empty()):
            if results.empty():
                await asyncio.sleep(0)
                continue
            garip = await results.get()
            await writer.writerow(
                [
                    garip.field,
                    garip.well,
                    garip.date,
                    "oil",
                    garip.method,
                    *garip.oil,
                ]
            )
            await writer.writerow(
                [
                    garip.field,
                    garip.well,
                    garip.date,
                    "liq",
                    garip.method,
                    *garip.liq,
                ]
            )


async def _handle_failures(
    path: Path,
    failures: asyncio.Queue[ProlongError],
    tasks: list[asyncio.Task],
) -> None:
    with LogContext(str(path), path / "errors.log") as logger:
        while not (all(task.done() for task in tasks) and failures.empty()):
            if failures.empty():
                await asyncio.sleep(0)
                continue
            gtm = await failures.get()
            await logger.aexception(
                "Не удалось обработать скважину: %s %s %s",
                gtm.field,
                gtm.well,
                gtm.date,
                gtm.method,
                exc_info=gtm.error,
            )


async def prolong_report(
    path: Path,
    expected: ProlongExpectedDAO,
    actual: Path,
    interpolations: list[Interpolation],
    pool: ProcessPoolManager,
    csv_config: CsvSettings,
) -> None:
    expected_values = await expected.get_all()
    results: asyncio.Queue[ProlongResult] = asyncio.Queue(maxsize=100)
    failures: asyncio.Queue[ProlongError] = asyncio.Queue(maxsize=100)
    with tempfile.TemporaryDirectory() as tmpdir:
        unpack_archive(actual, tmpdir)
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(
                    _process_well(
                        Path(tmpdir),
                        expected,
                        interpolation,
                        results,
                        failures,
                        pool,
                    )
                )
                for expected in expected_values
                for interpolation in interpolations
            ]
            tg.create_task(
                _handle_results(
                    path,
                    csv_config.encoding,
                    csv_config.delimiter,
                    results,
                    tasks,
                )
            )
            tg.create_task(_handle_failures(path, failures, tasks))
    make_archive(str(path), "zip", root_dir=path)
