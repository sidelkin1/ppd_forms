from datetime import date
from pathlib import Path
from shutil import make_archive

import pandas as pd

from app.core.utils.process_pool import ProcessPoolManager
from app.core.utils.save_dataframe import save_to_csv
from app.infrastructure.db.dao.sql.reporters.oil_loss import (
    FirstRateOilLossReporter,
    MaxRateOilLossReporter,
)
from app.infrastructure.files.config.models.csv import CsvSettings


def _calc_loss(df: pd.DataFrame) -> pd.DataFrame:
    df["start_oilcut"] = df["start_oil_rate"] / df["start_liq_rate"]
    df["end_oilcut"] = df["end_oil_rate"] / df["end_liq_rate"]
    df["start_oilcut"] = df["start_oilcut"].fillna(df["end_oilcut"].fillna(0))
    df["end_oilcut"] = df["end_oilcut"].fillna(df["start_oilcut"].fillna(0))
    df["dW"] = df["end_inj_rate"] - df["start_inj_rate"]
    df["dQoil"] = df["end_oil_rate"] - df["start_oil_rate"]
    df["dQoil(dQliq)"] = (
        0.5
        * (df["start_oilcut"] + df["end_oilcut"])
        * (df["end_liq_rate"] - df["start_liq_rate"])
    )
    df["dQoil(dWcut)"] = (
        0.5
        * (df["end_liq_rate"] + df["start_liq_rate"])
        * (df["end_oilcut"] - df["start_oilcut"])
    )
    df.drop(columns=["start_oilcut", "end_oilcut"], inplace=True)
    return df


def _process_data(df: pd.DataFrame, date_to: date) -> pd.DataFrame:
    df["end_dat_rep"] = df["end_dat_rep"].fillna(date_to)
    cols = ["end_oil_rate", "end_liq_rate", "end_watercut", "end_inj_rate"]
    df[cols] = df[cols].fillna(0)
    df = _calc_loss(df)
    return df


async def oil_loss_report(
    path: Path,
    date_from: date,
    date_to: date,
    dao: FirstRateOilLossReporter | MaxRateOilLossReporter,
    pool: ProcessPoolManager,
    csv_config: CsvSettings,
) -> None:
    df = await dao.read_one(date_from=date_from, date_to=date_to)
    df = await pool.run(_process_data, df, date_to)
    await save_to_csv(
        df, path / "oil_loss.csv", csv_config.encoding, csv_config.delimiter
    )
    make_archive(str(path), "zip", root_dir=path)
