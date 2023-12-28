from datetime import date
from pathlib import Path

import pandas as pd

from app.core.utils.process_pool import ProcessPoolManager
from app.core.utils.save_dataframe import save_to_csv
from app.infrastructure.db.dao.sql.reporters import OppPerYearReporter


def _process_data(df: pd.DataFrame) -> pd.DataFrame:
    df["reservoir"] = df["reservoir"].str.split(" ")
    df = df.explode("reservoir")
    grouper = [
        pd.Grouper(key="field"),
        pd.Grouper(key="reservoir"),
        pd.Grouper(key="well_type"),
        pd.Grouper(freq="YS", key="rec_date"),
    ]
    df = df.groupby(grouper, as_index=False).agg(["size", "nunique"])
    df["rec_date"] = df["rec_date"].dt.date
    return df


async def opp_per_year_report(
    path: Path,
    date_from: date,
    date_to: date,
    dao: OppPerYearReporter,
    pool: ProcessPoolManager,
) -> None:
    df = await dao.read_one(date_from=date_from, date_to=date_to)
    df = await pool.run(_process_data, df)
    await save_to_csv(df, path)
