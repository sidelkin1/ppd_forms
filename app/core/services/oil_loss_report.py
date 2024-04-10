from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.utils.process_pool import ProcessPoolManager
from app.core.utils.save_dataframe import save_to_csv
from app.infrastructure.db.dao.sql.reporters import (
    FirstRateLossReporter,
    MaxRateLossReporter,
)
from app.infrastructure.files.config.models.csv import CsvSettings


def _prepare_ns_ppd(df: pd.DataFrame, delimiter: str) -> pd.DataFrame:
    df["reservoir_neighbs"] = df["reservoir_neighbs"].fillna(df["reservoir"])
    df["reservoir"] = df["reservoir_neighbs"].str.split(delimiter)
    df.drop(columns=["reservoir_neighbs"], inplace=True)
    df = df.explode("reservoir")
    return df


def _prepare_inj_db(df: pd.DataFrame, delimiter: str) -> pd.DataFrame:
    df = df.assign(reservoir_all=df["reservoir"])
    df["reservoir"] = df["reservoir"].str.split(delimiter)
    df = df.explode("reservoir")
    return df


def _prepare_ns_oil(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("vnr_date").drop_duplicates(
        ["field", "well"], keep="last"
    )
    return df


def _gather_neighbs(
    df_inj_db: pd.DataFrame,
    df_ns_ppd: pd.DataFrame,
    df_neighbs: pd.DataFrame,
    delimiter: str,
) -> pd.DataFrame:
    df = pd.merge(
        _prepare_inj_db(df_inj_db, delimiter),
        _prepare_ns_ppd(df_ns_ppd, delimiter),
        on=["field", "well", "reservoir"],
        how="left",
    )
    df = pd.merge(
        df,
        df_neighbs,
        on=["field", "well", "reservoir"],
        how="left",
        suffixes=("", "_gid"),
    )
    df["neighbs"] = df["neighbs"].fillna(df["neighbs_gid"])
    df.drop(columns=["neighbs_gid"], inplace=True)
    df["gtm_date"] = df["gtm_date"].fillna("")
    df["gtm_group"] = df["gtm_group"].fillna("")
    df["neighbs"] = df["neighbs"].fillna("")
    df["neighbs"] = df["neighbs"].str.split(delimiter)
    df = df.explode("neighbs")
    return df


def _join_ns_oil(df: pd.DataFrame, df_ns: pd.DataFrame) -> pd.DataFrame:
    df = pd.merge(
        df,
        _prepare_ns_oil(df_ns),
        left_on=["field", "neighbs"],
        right_on=["field", "well"],
        how="left",
        suffixes=("", "_ns_oil"),
    )
    df["vnr_date"] = df["vnr_date"].fillna("")
    df["gtm_name"] = df["gtm_name"].fillna("")
    df.drop(columns=["well_ns_oil"], inplace=True)
    return df


def _join_inj_mer(
    df: pd.DataFrame, df_mer: pd.DataFrame, period: str
) -> pd.DataFrame:
    crit = (df_mer["period"] == period) & (df_mer["inj_rate"] > 0)
    on_cols = ["field", "well", "reservoir"]
    cols = [*on_cols, "dat_rep", "inj_rate"]
    df = pd.merge(
        df,
        df_mer.loc[crit, cols],
        on=on_cols,
        how="left",
        suffixes=("", "_mer"),
    )
    df["dat_rep_mer"] = df["dat_rep_mer"].fillna("")
    df["inj_rate"] = df["inj_rate"].fillna(0)
    df.rename(
        columns={
            "dat_rep_mer": f"{period}_inj_date",
            "inj_rate": f"{period}_inj_rate",
        },
        inplace=True,
    )
    return df


def _join_prod_mer(
    df: pd.DataFrame, df_mer: pd.DataFrame, period: str
) -> pd.DataFrame:
    crit = (df_mer["period"] == period) & (df_mer["liq_rate"] > 0)
    left_on_cols = ["field", "neighbs", "reservoir"]
    right_in_cols = ["field", "well", "reservoir"]
    cols = [*right_in_cols, "dat_rep", "oil_rate", "liq_rate", "watercut"]
    df = pd.merge(
        df,
        df_mer.loc[crit, cols],
        left_on=left_on_cols,
        right_on=right_in_cols,
        how="left",
        suffixes=("", "_mer"),
    )
    df["dat_rep_mer"] = df["dat_rep_mer"].fillna("")
    df["oil_rate"] = df["oil_rate"].fillna(0)
    df["liq_rate"] = df["liq_rate"].fillna(0)
    df["watercut"] = df["watercut"].fillna(0)
    df.drop(columns=["well_mer"], inplace=True)
    df.rename(
        columns={
            "dat_rep_mer": f"{period}_prod_date",
            "oil_rate": f"{period}_oil_rate",
            "liq_rate": f"{period}_liq_rate",
            "watercut": f"{period}_watercut",
        },
        inplace=True,
    )
    return df


def _join_mer(df: pd.DataFrame, df_mer: pd.DataFrame) -> pd.DataFrame:
    df = _join_inj_mer(df, df_mer, "start")
    df = _join_inj_mer(df, df_mer, "end")
    df = _join_prod_mer(df, df_mer, "start")
    df = _join_prod_mer(df, df_mer, "end")
    return df


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


def _agg_oil_loss(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["field", "well", "neighbs"]
    d: dict[str, Any] = {
        "neighbs_loss_all": ("dQoil", "sum"),
        "neighbs_loss_liq": ("dQoil(dQliq)", "sum"),
        "neighbs_loss_wcut": ("dQoil(dWcut)", "sum"),
    }
    return (
        df.loc[df["neighbs"] != "", :].groupby(cols, as_index=False).agg(**d)
    )


def _format_neighbs_loss(df: pd.DataFrame) -> pd.DataFrame:
    for neighbs in [
        "neighbs_loss_all",
        "neighbs_loss_liq",
        "neighbs_loss_wcut",
    ]:
        df[neighbs] = df[["neighbs", neighbs]].agg(
            lambda s: "{} ({:.1f})".format(*s), axis=1
        )
    return df


def _agg_neighbs_loss(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["field", "well"]
    d: dict[str, Any] = {
        "neighbs_loss_all": lambda s: s.str.cat(sep=","),
        "neighbs_loss_liq": lambda s: s.str.cat(sep=","),
        "neighbs_loss_wcut": lambda s: s.str.cat(sep=","),
    }
    return df.groupby(cols, as_index=False).agg(d)


def _join_pivot(df: pd.DataFrame) -> pd.DataFrame:
    df_pivot = _agg_oil_loss(df)
    df_pivot = _format_neighbs_loss(df_pivot)
    df_pivot = _agg_neighbs_loss(df_pivot)
    df = pd.merge(df, df_pivot, on=["field", "well"], how="left")
    df["neighbs_loss_all"] = df["neighbs_loss_all"].fillna("")
    df["neighbs_loss_liq"] = df["neighbs_loss_liq"].fillna("")
    df["neighbs_loss_wcut"] = df["neighbs_loss_wcut"].fillna("")
    return df


def _process_data(
    dfs: dict[str, pd.DataFrame], delimiter: str
) -> pd.DataFrame:
    df = _gather_neighbs(
        dfs["inj_db"], dfs["ns_ppd"], dfs["neighbs"], delimiter
    )
    df = _join_ns_oil(df, dfs["ns_oil"])
    df = _join_mer(df, dfs["mer"])
    df = _calc_loss(df)
    df = _join_pivot(df)
    return df


async def oil_loss_report(
    path: Path,
    date_from: date,
    date_to: date,
    dao: FirstRateLossReporter | MaxRateLossReporter,
    pool: ProcessPoolManager,
    delimiter: str,
    csv_config: CsvSettings,
) -> None:
    dfs = await dao.read_all(date_from=date_from, date_to=date_to)
    df = await pool.run(_process_data, dfs, delimiter)
    await save_to_csv(df, path, csv_config.encoding, csv_config.delimiter)
