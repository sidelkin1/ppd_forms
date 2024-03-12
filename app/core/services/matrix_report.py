from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config.settings import Settings
from app.core.models.enums import ExcludeGTM
from app.core.utils.process_pool import ProcessPoolManager
from app.core.utils.save_dataframe import save_to_csv
from app.infrastructure.db.dao.sql.reporters import MatrixReporter


def _add_months(s: pd.Series, n: int) -> pd.Series:
    s = pd.to_datetime(s, errors="coerce")
    crit = s.dt.is_month_start
    s[~crit] += pd.offsets.MonthBegin(n=-1)  # type: ignore[operator]
    s += pd.offsets.MonthBegin(n=n)  # type: ignore[operator]
    return s.dt.date


def _expand_date_range(
    df: pd.DataFrame, left: str, right: str, result: str
) -> pd.DataFrame:
    df[result] = df[[left, right]].agg(
        lambda s: pd.date_range(start=s[left], end=s[right], freq="MS").date,
        axis=1,
    )
    df = df.explode(result)
    return df


def _expand_reservoir(df: pd.DataFrame, delimiter: str) -> pd.DataFrame:
    df["reservoir_neighbs"] = df["reservoir_neighbs"].fillna(df["reservoir"])
    df = df.assign(reservoir_all=df["reservoir_neighbs"])
    df["reservoir"] = df["reservoir_neighbs"].str.split(delimiter)
    df.drop(columns=["reservoir_neighbs"], inplace=True)
    df = df.explode("reservoir")
    return df


def _expand_neighbs(df: pd.DataFrame, delimiter: str) -> pd.DataFrame:
    df["neighbs"] = df["neighbs"].str.split(delimiter)
    df = df.explode("neighbs")
    return df


def _expand_date_pred(
    df: pd.DataFrame, base_period: int, pred_period: int
) -> pd.DataFrame:
    num_pred = df.shape[0] * list(range(-base_period, pred_period))
    df["date_base"] = _add_months(df["gtm_date"], -base_period)
    df["date_to"] = _add_months(df["gtm_date"], pred_period - 1)
    df = _expand_date_range(df, "date_base", "date_to", "date_pred")
    df.drop(columns=["date_to"], inplace=True)
    df = df.assign(num_pred=num_pred)
    return df


def _prepare_ns_ppd(
    df: pd.DataFrame, delimiter: str, base_period: int, pred_period: int
) -> pd.DataFrame:
    df = _expand_reservoir(df, delimiter)
    df = _expand_neighbs(df, delimiter)
    df = _expand_date_pred(df, base_period, pred_period)
    return df


def _prepare_ns_oil(df: pd.DataFrame) -> pd.DataFrame:
    df["start_date"] = _add_months(df["start_date"], 0)
    df["vnr_date"] = _add_months(df["vnr_date"], 0)
    df = _expand_date_range(df, "start_date", "vnr_date", "date_pred")
    df.drop(columns=["start_date", "vnr_date"], inplace=True)
    cols = ["field", "well", "date_pred"]
    df = df.groupby(cols, as_index=False).agg(
        {"gtm_name": lambda s: s.str.cat(sep=",")}
    )
    return df


def _join_ns_oil(df: pd.DataFrame, df_ns: pd.DataFrame) -> pd.DataFrame:
    df = pd.merge(
        left=df,
        right=df_ns,
        left_on=["field", "neighbs", "date_pred"],
        right_on=["field", "well", "date_pred"],
        how="left",
        suffixes=["", "_oil"],
    )
    df.drop(columns=["well_oil"], inplace=True)
    df["gtm_name"] = df["gtm_name"].fillna("")
    return df


def _get_base_neighbs(df: pd.DataFrame, delete_gtm: str) -> pd.DataFrame:
    if delete_gtm:
        df["delete_gtm"] = df["gtm_name"].str.contains(delete_gtm, na=False)
        cols = ["field", "well", "reservoir", "gtm_date", "neighbs"]
        df["delete_gtm"] = df.groupby(cols)["delete_gtm"].transform("any")
        df["neighbs_base"] = df.loc[~df["delete_gtm"], "neighbs"]
        df["neighbs_base"] = df["neighbs_base"].fillna("")
    else:
        df["delete_gtm"] = False
        df["neighbs_base"] = df["neighbs"]
    return df


def _fill_cum_values(df: pd.DataFrame, column: str) -> pd.DataFrame:
    cols = ["field", "well", "reservoir", "gtm_date", "neighbs"]
    df[column] = df.groupby(cols)[column].ffill()
    df[column] = df.groupby(cols)[column].bfill()  # FIXME bad decision
    df[column] = df[column].fillna(0)
    return df


def _divide_inj_neighbs(
    df: pd.DataFrame, period: str, columns: list[str]
) -> pd.DataFrame:
    cols = ["field", "well", "reservoir", "gtm_date", f"date_{period}"]
    size = df.groupby(cols)["neighbs"].transform("size")
    df[columns] = df[columns].div(size, axis=0)
    return df


def _join_inj_mer(
    df: pd.DataFrame, df_mer: pd.DataFrame, period: str
) -> pd.DataFrame:
    left_on = ["field", "well", "reservoir", f"date_{period}"]
    right_on = ["field", "well", "reservoir", "dat_rep"]
    cols = [*right_on, "inj_rate", "water", "cum_water"]
    df = pd.merge(
        df, df_mer[cols], left_on=left_on, right_on=right_on, how="left"
    )
    df.drop(columns=["dat_rep"], inplace=True)
    df["inj_rate"] = df["inj_rate"].fillna(0)
    df["water"] = df["water"].fillna(0)
    df = _fill_cum_values(df, "cum_water")
    df = _divide_inj_neighbs(df, period, ["inj_rate", "water", "cum_water"])
    df.rename(
        columns={
            "inj_rate": f"{period}_inj_rate",
            "water": f"{period}_water",
            "cum_water": f"{period}_cum_water",
        },
        inplace=True,
    )
    return df


def _join_prod_mer(
    df: pd.DataFrame, df_mer: pd.DataFrame, period: str
) -> pd.DataFrame:
    left_on = ["field", "neighbs_base", "reservoir", f"date_{period}"]
    right_on = ["field", "well", "reservoir", "dat_rep"]
    cols = [
        *right_on,
        "oil_rate",
        "liq_rate",
        "watercut",
        "liquid_res",
        "cum_liquid_res",
    ]
    df = pd.merge(
        df,
        df_mer[cols],
        left_on=left_on,
        right_on=right_on,
        how="left",
        suffixes=["", "_mer"],
    )
    df.drop(columns=["dat_rep", "well_mer"], inplace=True)
    df["oil_rate"] = df["oil_rate"].fillna(0)
    df["liq_rate"] = df["liq_rate"].fillna(0)
    df["watercut"] = df["watercut"].fillna(0)
    df["liquid_res"] = df["liquid_res"].fillna(0)
    df = _fill_cum_values(df, "cum_liquid_res")
    df.rename(
        columns={
            "oil_rate": f"{period}_oil_rate",
            "liq_rate": f"{period}_liq_rate",
            "watercut": f"{period}_watercut",
            "liquid_res": f"{period}_liquid_res",
            "cum_liquid_res": f"{period}_cum_liquid_res",
        },
        inplace=True,
    )
    return df


def _calc_loss(df: pd.DataFrame) -> pd.DataFrame:
    df["base_oilcut"] = df["base_oil_rate"] / df["base_liq_rate"]
    df["pred_oilcut"] = df["pred_oil_rate"] / df["pred_liq_rate"]
    df["base_oilcut"] = df["base_oilcut"].fillna(df["pred_oilcut"].fillna(0))
    df["pred_oilcut"] = df["pred_oilcut"].fillna(df["base_oilcut"].fillna(0))
    df["dQoil"] = df["pred_oil_rate"] - df["base_oil_rate"]
    df["dQoil(dQliq)"] = (
        0.5
        * (df["base_oilcut"] + df["pred_oilcut"])
        * (df["pred_liq_rate"] - df["base_liq_rate"])
    )
    df["dQoil(dWcut)"] = (
        0.5
        * (df["pred_liq_rate"] + df["base_liq_rate"])
        * (df["pred_oilcut"] - df["base_oilcut"])
    )
    df.drop(columns=["base_oilcut", "pred_oilcut"], inplace=True)
    return df


def _agg_oil_loss(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["field", "well", "gtm_date", "neighbs", "date_pred"]
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
    cols = ["field", "well", "gtm_date", "date_pred"]
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
    df = pd.merge(
        df, df_pivot, on=["field", "well", "gtm_date", "date_pred"], how="left"
    )
    df["neighbs_loss_all"] = df["neighbs_loss_all"].fillna("")
    df["neighbs_loss_liq"] = df["neighbs_loss_liq"].fillna("")
    df["neighbs_loss_wcut"] = df["neighbs_loss_wcut"].fillna("")
    return df


def _find_effect_end(df: pd.DataFrame, on_date: date) -> pd.DataFrame:
    cols = ["field", "well", "gtm_date"]
    df_end = df[cols].drop_duplicates().sort_values(cols)
    df_end["effect_end"] = _add_months(df_end["gtm_date"], 0)
    df_end["effect_end"] = df_end.groupby(["field", "well"])[
        "effect_end"
    ].shift(periods=-1, fill_value=on_date)
    return df_end


def _join_effect_end(df: pd.DataFrame, on_date: date) -> pd.DataFrame:
    df_end = _find_effect_end(df, on_date)
    left_on = ["field", "well", "gtm_date", "date_pred"]
    right_on = ["field", "well", "gtm_date", "effect_end"]
    df = pd.merge(df, df_end, left_on=left_on, right_on=right_on, how="left")
    df["effect_end"] = df["effect_end"].notna()
    return df


def _process_data(
    dfs: dict[str, pd.DataFrame],
    base_period: int,
    pred_period: int,
    excludes: list[ExcludeGTM],
    on_date: date,
    delimiter: str,
) -> pd.DataFrame:
    delete_gtm = "|".join(excludes)
    df = _prepare_ns_ppd(dfs["ns_ppd"], delimiter, base_period, pred_period)
    df = _join_ns_oil(df, _prepare_ns_oil(dfs["ns_oil"]))
    df = _get_base_neighbs(df, delete_gtm)
    df = _join_inj_mer(df, dfs["mer"], "base")
    df = _join_inj_mer(df, dfs["mer"], "pred")
    df = _join_prod_mer(df, dfs["mer"], "base")
    df = _join_prod_mer(df, dfs["mer"], "pred")
    df = _calc_loss(df)
    df = _join_pivot(df)
    df = _join_effect_end(df, on_date)
    return df


async def matrix_report(
    path: Path,
    date_from: date,
    date_to: date,
    base_period: int,
    pred_period: int,
    excludes: list[ExcludeGTM],
    on_date: date,
    dao: MatrixReporter,
    pool: ProcessPoolManager,
    settings: Settings,
) -> None:
    dfs = await dao.read_all(
        date_from=date_from,
        date_to=date_to,
        base_period=base_period,
        pred_period=pred_period,
    )
    df = await pool.run(
        _process_data,
        dfs,
        base_period,
        pred_period,
        excludes,
        on_date,
        settings.delimiter,
    )
    await save_to_csv(df, path, settings.csv_encoding, settings.csv_delimiter)
