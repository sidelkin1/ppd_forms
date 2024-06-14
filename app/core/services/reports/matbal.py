from datetime import date
from pathlib import Path
from shutil import make_archive

import openpyxl
import pandas as pd
from openpyxl.writer.excel import save_workbook

from app.core.models.dto import UneftFieldDB, UneftReservoirDB
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.dao.complex.reporters import MatbalReporter

_EXCEL_RATE_START_ROW = 15
_EXCEL_RATE_START_COLUMN = 2
_EXCEL_RATE_LAST_COLUMN = 6


def _expand_date_range(
    df: pd.DataFrame, left: date, right: date, result: str
) -> pd.DataFrame:
    df[result] = pd.date_range(start=left, end=right, freq="MS").date
    df = df.explode(result)
    return df


def _join_rates_and_measurements(
    df: pd.DataFrame, rates: pd.DataFrame, measurements: pd.DataFrame | None
) -> pd.DataFrame:
    df = pd.merge(df, rates, how="left", on="date").fillna(0)
    if measurements is not None:
        df = pd.merge(df, measurements, how="left", on="date")
    else:
        df = df.assign(Pres=None)
    return df


def _fill_template(df: pd.DataFrame, path: Path, template: Path) -> None:
    result = path / template.name
    try:
        wb = openpyxl.load_workbook(template, keep_vba=True)
        ws = wb["MB_simple"]
        for row, df_row in zip(
            ws.iter_rows(
                min_row=_EXCEL_RATE_START_ROW,
                min_col=_EXCEL_RATE_START_COLUMN,
                max_col=_EXCEL_RATE_LAST_COLUMN,
                max_row=df.shape[0] + _EXCEL_RATE_START_ROW - 1,
            ),
            df.itertuples(index=False),
        ):
            for cell, value in zip(row, df_row):
                cell.value = value
        save_workbook(wb, result)
    finally:
        wb.close()


def _process_data(
    rates: pd.DataFrame,
    measurements: pd.DataFrame | None,
    path: Path,
    template: Path,
) -> pd.DataFrame:
    df = pd.DataFrame(columns=["date"])
    df = _expand_date_range(
        df, rates["date"].min(), rates["date"].max(), "date"
    )
    df = _join_rates_and_measurements(df, rates, measurements)
    _fill_template(df, path, template)
    df.to_csv(path / "matbal.csv", sep=";")
    return df


async def matbal_report(
    path: Path,
    template: Path,
    field: UneftFieldDB,
    reservoirs: list[UneftReservoirDB],
    alternative: bool,
    dao: MatbalReporter,
    pool: ProcessPoolManager,
) -> None:
    reservoir_names = [reservoir.name for reservoir in reservoirs]
    rates = await dao.get_rates(field.id, reservoir_names, alternative)
    measurements = await dao.get_measurements()
    await pool.run(_process_data, rates, measurements, path, template)
    make_archive(str(path), "zip", root_dir=path)
