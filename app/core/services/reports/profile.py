from datetime import date
from pathlib import Path
from shutil import make_archive

import pandas as pd

from app.core.utils.process_pool import ProcessPoolManager
from app.core.utils.save_dataframe import save_to_csv
from app.infrastructure.db.dao.sql.reporters import WellProfileReporter
from app.infrastructure.files.config.models.csv import CsvSettings


def _group_diff_absorb(df: pd.DataFrame) -> pd.DataFrame:
    columns = df.columns.difference(["diff_absorp", "remarks"], sort=False)
    df["diff_absorp"] /= df.groupby(level=0)["diff_absorp"].transform(len)
    return df.groupby(columns.to_list(), as_index=False).agg(
        {
            "diff_absorp": "sum",
            "remarks": (
                lambda s: s[s.str.contains(r"\w+", na=False)]
                .drop_duplicates()
                .str.cat(sep=",")
            ),
        }
    )


def _calc_layer_rate(df: pd.DataFrame, rate: str) -> pd.DataFrame:
    df = df.eval(f"{rate}_layer={rate}_all*diff_absorp/100")
    df[f"{rate}_layer"] = df[f"{rate}_layer"].fillna(df[rate])
    df[rate] = df[rate].mul(df["1/num_layer"], fill_value=1)
    return df


def _calc_layer_rates(df: pd.DataFrame) -> pd.DataFrame:
    columns = ["field", "well_name", "cid", "rec_date"]
    df["1/num_layer"] = 1 / df.groupby(columns)["layer"].transform(len)
    df = _calc_layer_rate(df, "liq_rate")
    df = _calc_layer_rate(df, "inj_rate")
    return df


def _process_data(df: pd.DataFrame, delimiter: str) -> pd.DataFrame:
    df["layer"] = df["layer"].str.split(delimiter)
    df = df.explode("layer")
    df["layer"] = df["layer"].fillna("")
    df = _group_diff_absorb(df)
    df = _calc_layer_rates(df)
    return df


async def profile_report(
    path: Path,
    date_from: date,
    date_to: date,
    dao: WellProfileReporter,
    pool: ProcessPoolManager,
    delimiter: str,
    csv_config: CsvSettings,
) -> None:
    df = await dao.read_one(date_from=date_from, date_to=date_to)
    df = await pool.run(_process_data, df, delimiter)
    await save_to_csv(
        df, path / "profile.csv", csv_config.encoding, csv_config.delimiter
    )
    make_archive(str(path), "zip", root_dir=path)
