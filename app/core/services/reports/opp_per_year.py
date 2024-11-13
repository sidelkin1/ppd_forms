from datetime import date
from pathlib import Path
from shutil import make_archive

import pandas as pd

from app.core.utils.process_pool import ProcessPoolManager
from app.core.utils.save_dataframe import save_to_csv
from app.infrastructure.db.dao.sql.reporters import OppPerYearReporter
from app.infrastructure.files.config.models.csv import CsvSettings


def _get_per_well(df: pd.DataFrame) -> pd.DataFrame:
    per_well = df.drop_duplicates().copy()
    per_well["rec_date"] = per_well["rec_date"].dt.date
    return per_well


def _get_per_year(df: pd.DataFrame) -> pd.DataFrame:
    grouper = [
        pd.Grouper(key="field"),
        pd.Grouper(key="reservoir"),
        pd.Grouper(key="well_type"),
        pd.Grouper(freq="YS", key="rec_date"),
    ]
    per_year = df.groupby(grouper, as_index=False).agg(["size", "nunique"])
    per_year["rec_date"] = per_year["rec_date"].dt.date
    return per_year


def _process_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df["reservoir"] = df["reservoir"].str.split(" ")
    df = df.explode("reservoir")
    per_well = _get_per_well(df)
    per_year = _get_per_year(df)
    return per_well, per_year


async def opp_per_year_report(
    path: Path,
    date_from: date,
    date_to: date,
    dao: OppPerYearReporter,
    pool: ProcessPoolManager,
    csv_config: CsvSettings,
) -> None:
    df = await dao.read_one(date_from=date_from, date_to=date_to)
    per_well, per_year = await pool.run(_process_data, df)
    await save_to_csv(
        per_well,
        path / "opp_per_well.csv",
        csv_config.encoding,
        csv_config.delimiter,
    )
    await save_to_csv(
        per_year,
        path / "opp_per_year.csv",
        csv_config.encoding,
        csv_config.delimiter,
    )
    make_archive(str(path), "zip", root_dir=path)
