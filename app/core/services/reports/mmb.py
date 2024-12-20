import asyncio
from datetime import date
from pathlib import Path
from shutil import make_archive

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

from app.core.config.models.mmb import MmbSettings
from app.core.utils.process_pool import ProcessPoolManager
from app.core.utils.save_dataframe import save_to_csv
from app.infrastructure.db.dao.complex.reporters import MmbReporter
from app.infrastructure.files.config.models.csv import CsvSettings


def _get_zero_time(df: pd.DataFrame) -> date:
    return df["Date"].min() - relativedelta(months=1)


def _tank_mapping(df: pd.DataFrame) -> pd.Series:
    return pd.Series(df["Tank"].to_numpy(), index=df["Well"])


def _get_uids(descr: pd.DataFrame, delimiter: str) -> pd.DataFrame:
    cols = ["Field", "Well", "Reservoir"]
    df = descr[cols].sort_values(cols)
    df["Reservoir"] = df["Reservoir"].str.split(delimiter)
    return df.explode("Reservoir")


def _expand_date_range(
    df: pd.DataFrame, left: date, right: date, result: str
) -> pd.DataFrame:
    df[result] = [
        pd.date_range(start=left, end=right, freq="MS").date
    ] * df.shape[0]
    df = df.explode(result)
    return df


def _join_mer(
    df: pd.DataFrame, rates: pd.DataFrame, zero_time: date
) -> pd.DataFrame:
    df = _expand_date_range(df, zero_time, rates["Date"].max(), "Date")
    df = pd.merge(
        df, rates, on=["Field", "Well", "Reservoir", "Date"], how="left"
    )
    return df


def _prepare_resp(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Field", "Well", "Reservoir", "Date"]
    return df.groupby(cols, as_index=False).agg(
        {
            "Pres": "mean",
            "Source_resp": lambda s: s.drop_duplicates().str.cat(sep=","),
        }
    )


def _join_resp(df: pd.DataFrame, resp: pd.DataFrame) -> pd.DataFrame:
    resp = _prepare_resp(resp)
    df = pd.merge(
        df, resp, on=["Field", "Well", "Reservoir", "Date"], how="left"
    )
    return df


def _prepare_bhp(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Field", "Well", "Reservoir", "Date"]
    return df.groupby(cols, as_index=False).agg(
        {
            "Pbhp": "mean",
            "Source_bhp": lambda s: s.drop_duplicates().str.cat(sep=","),
        }
    )


def _join_bhp(df: pd.DataFrame, bhp: pd.DataFrame) -> pd.DataFrame:
    bhp = _prepare_bhp(bhp)
    df = pd.merge(
        df, bhp, on=["Field", "Well", "Reservoir", "Date"], how="left"
    )
    return df


def _prepare_works(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Field", "Well", "Reservoir", "Date"]
    return df.groupby(cols, as_index=False).agg(
        {
            "Wellwork": lambda s: s.drop_duplicates().str.cat(sep=","),
        }
    )


def _join_works(df: pd.DataFrame, works: pd.DataFrame) -> pd.DataFrame:
    works = _prepare_works(works)
    df = pd.merge(
        df, works, on=["Field", "Well", "Reservoir", "Date"], how="left"
    )
    return df


def _join_scal(df: pd.DataFrame, descr: pd.DataFrame) -> pd.DataFrame:
    cols = ["Field", "Well"]
    idx = ["muw", "muo", "krw_max", "kro_max"]
    df = df.merge(descr[cols + idx], on=cols, how="left")
    return df


def _split_bhp(df: pd.DataFrame) -> pd.DataFrame:
    # Разбиваем замеры Рзаб на добычу и закачку.
    # Два случая обрабатываются потом отдельно после
    # группировки блоков:
    # 1. Одновременная добыча и закачка (см. `_correct_ambiguity`)
    # 2. Неучтенные замеры Рзаб (см. `_refill_bhp`)
    crit_prod = df[["Qoil", "Qwat"]].sum(axis=1) > 0
    loc = df.columns.get_loc("Pbhp")
    df.insert(loc, "Pbhp_prod", df.loc[crit_prod, "Pbhp"])
    crit_inj = df["Qinj"] > 0
    df.insert(loc + 1, "Pbhp_inj", df.loc[crit_inj, "Pbhp"])
    df["Ambiguity"] = crit_prod & crit_inj
    df.loc[crit_prod | crit_inj, "Pbhp"] = np.nan
    return df


def _map_wells(
    df: pd.DataFrame, to_tank: pd.Series, well: str, tank: str | None = None
) -> pd.DataFrame:
    df[well] = df[well].map(to_tank)
    if tank is not None:
        df.rename(columns={well: "Tank"}, inplace=True)
    return df


def _prepare_rates(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Source_resp", "Source_bhp", "Wellwork"]
    for col in cols:
        is_empty = df[col] == ""
        df[col] = df["Tank"].str.cat(df[col], sep=": ")
        df.loc[is_empty, col] = ""
    return df


def _group_reservoirs(df: pd.DataFrame) -> pd.DataFrame:
    df = _prepare_rates(df)
    cols = ["Field", "Tank", "Date"]
    names = df.columns
    df = (
        df.groupby(cols, as_index=False)
        .agg(
            {
                "Reservoir": lambda s: (
                    s.str.split(r"[^\w+\-()]+")
                    .explode()
                    .drop_duplicates()
                    .sort_values()
                    .str.cat(sep=",")
                ),
                "Qoil": "sum",
                "Qwat": "sum",
                "Qinj": "sum",
                "Pres": "mean",
                "Source_resp": lambda s: (
                    s[s != ""].drop_duplicates().str.cat(sep=",")
                ),
                "Pbhp": "mean",
                "Pbhp_prod": "mean",
                "Pbhp_inj": "mean",
                "Source_bhp": lambda s: (
                    s[s != ""].drop_duplicates().str.cat(sep=",")
                ),
                "Wellwork": lambda s: (
                    s[s != ""].drop_duplicates().str.cat(sep=",")
                ),
                "Ambiguity": "any",
                "muw": "mean",
                "muo": "mean",
                "krw_max": "mean",
                "kro_max": "mean",
            }
        )
        .reindex(columns=names)
    )
    return df


def _refill_bhp(df: pd.DataFrame) -> pd.DataFrame:
    # Повторно заполняем Рзаб для случаев, когда
    # замер Рзаб был на один объект (например, официальный),
    # а добыча (закачка) велась с другого объекта (например, НЛД)
    crit = df[["Qoil", "Qwat"]].sum(axis=1) > 0
    df.loc[crit, "Pbhp_prod"] = df.loc[crit, "Pbhp_prod"].fillna(
        df.loc[crit, "Pbhp"]
    )
    crit = df["Qinj"] > 0
    df.loc[crit, "Pbhp_inj"] = df.loc[crit, "Pbhp_inj"].fillna(
        df.loc[crit, "Pbhp"]
    )
    df.drop(columns="Pbhp", inplace=True)
    return df


def _calc_liquid(df: pd.DataFrame) -> pd.DataFrame:
    loc = df.columns.get_loc("Qwat")
    Qliq = df["Qoil"] + df["Qwat"]
    df.insert(loc=loc + 1, column="Qliq", value=Qliq)
    return df


def _calc_daily_rates(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Qoil", "Qwat", "Qliq", "Qinj"]
    days = pd.to_datetime(df["Date"]).dt.daysinmonth
    df[cols] = df[cols].div(days, axis=0)
    return df


def _calc_watercut(df: pd.DataFrame) -> pd.DataFrame:
    df["Wcut"] = df["Qwat"] / df["Qliq"]
    cols = ["Field", "Tank"]
    df["Wcut"] = df.groupby(cols)["Wcut"].transform(
        lambda s: s.ffill().bfill().fillna(1)
    )
    return df


def _calc_total_mobility(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["muw", "muo", "krw_max", "kro_max"]
    df["Total_mobility"] = df["krw_max"] / df["muw"] * df["Wcut"]
    df["Total_mobility"] += df["kro_max"] / df["muo"] * (1 - df["Wcut"])
    df.drop(columns=cols, inplace=True)
    return df


def _add_weights(df: pd.DataFrame, mmb_config: MmbSettings) -> pd.DataFrame:
    df.loc[df["Pres"].notna(), "Wres"] = 1
    df.loc[df["Pbhp_prod"].notna(), "Wbhp_prod"] = 1
    df.loc[df["Pbhp_inj"].notna(), "Wbhp_inj"] = 1
    df["Pres_min"] = df["Pbhp_prod"] + mmb_config.press_tol.min_value
    df["Pres_max"] = df["Pbhp_inj"] - mmb_config.press_tol.max_value
    return df


def _correct_ambiguity(df: pd.DataFrame) -> pd.DataFrame:
    # В случае, если на какой-то месяц есть одновременно и добыча, и закачка,
    # то исключаем Рзаб (и соответственно ограничения на Рпл)
    # из расчета на этот месяц
    cols = ["Wbhp_prod", "Wbhp_inj", "Pres_min", "Pres_max"]
    df.loc[df["Ambiguity"], cols] = np.nan
    df.drop(columns="Ambiguity", inplace=True)
    return df


def _finish_rates(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Qoil", "Qwat", "Qliq", "Qinj"]
    df[cols] = df[cols].fillna(0)
    cols = [
        "Pres",
        "Pbhp_prod",
        "Pbhp_inj",
        "Pres_min",
        "Pres_max",
        "Wres",
        "Wbhp_prod",
        "Wbhp_inj",
        "Total_mobility",
    ]
    df[cols] = df[cols].fillna("")
    return df


def _calc_rates(
    descr: pd.DataFrame,
    uids: pd.DataFrame,
    hist: dict[str, pd.DataFrame],
    to_tank: pd.Series,
    zero_time: date,
    mmb_config: MmbSettings,
) -> pd.DataFrame:
    df = _join_mer(uids, hist["rates"], zero_time)
    df = _join_resp(df, hist["resp"])
    df = _join_bhp(df, hist["bhp"])
    df = _join_works(df, hist["works"])
    df = _join_scal(df, descr)
    df = _map_wells(df, to_tank, "Well", "Tank")
    df = _split_bhp(df)
    df = _group_reservoirs(df)
    df = _refill_bhp(df)
    df = _calc_liquid(df)
    df = _calc_daily_rates(df)
    df = _calc_watercut(df)
    df = _calc_total_mobility(df)
    df = _add_weights(df, mmb_config)
    df = _correct_ambiguity(df)
    df = _finish_rates(df)
    return df


def _prepare_connections(
    descr: pd.DataFrame, to_tank: pd.Series
) -> pd.DataFrame:
    df = descr[["Field", "Well", "Reservoir", "Neighb", "T"]].copy()
    df["Neighb"] = df["Neighb"].str.split(r"\W+")
    df = df.explode("Neighb").dropna()
    df = _map_wells(df, to_tank, "Well", "Tank")
    df = _map_wells(df, to_tank, "Neighb")
    return df


def _filter_connections(
    df: pd.DataFrame, left: str, right: str
) -> pd.DataFrame:
    cols = [left, right]
    df[cols] = df[cols].apply(np.sort, axis=1, raw=True)
    df = df[df[left] != df[right]].drop_duplicates(subset=cols)
    return df


def _insert_columns(df: pd.DataFrame, zero_time: date) -> pd.DataFrame:
    loc = df.columns.get_loc("Neighb")
    df.insert(loc=loc + 1, column="Parameter", value="Tconn")
    df.insert(loc=loc + 2, column="Date", value=zero_time)
    df.rename(columns={"T": "Init_value"}, inplace=True)
    return df


def _get_connections(
    descr: pd.DataFrame, to_tank: pd.Series, zero_time: date
) -> pd.DataFrame:
    df = _prepare_connections(descr, to_tank)
    df = _filter_connections(df, "Tank", "Neighb")
    df = _insert_columns(df, zero_time)
    return df


def _prepare_params(descr: pd.DataFrame) -> pd.DataFrame:
    df = descr.drop(columns=["Well", "Neighb", "T"])
    cols = ["Pi", "Bwi", "Boi", "cw", "co", "cf", "Swi"]
    df[cols] = df[cols].mul(df["Vpi"], axis=0)
    d = {
        "Reservoir": lambda s: (
            s.str.split(r"[^\w+\-()]+")
            .explode()
            .drop_duplicates()
            .sort_values()
            .str.cat(sep=",")
        ),
        "Pi": "sum",
        "Bwi": "sum",
        "Boi": "sum",
        "cw": "sum",
        "co": "sum",
        "cf": "sum",
        "Swi": "sum",
        "Vpi": "sum",
        "Tconst": "mean",
        "Prod_index": "mean",
        "Inj_index": "mean",
        "Frac_inj": "mean",
        "Min_Pres": "min",
        "Max_Pres": "max",
        "muw": "mean",
        "muo": "mean",
        "krw_max": "mean",
        "kro_max": "mean",
    }
    df = df.groupby(["Field", "Tank"], as_index=False).agg(d)  # type: ignore
    df[cols] = df[cols].div(df["Vpi"], axis=0)
    return df


def _unstack_params(df: pd.DataFrame, zero_time: date) -> pd.DataFrame:
    cols = ["Field", "Tank", "Reservoir"]
    params = df.columns[len(cols) :].to_list()
    df = pd.melt(
        df,
        id_vars=cols,
        value_vars=params,
        var_name="Parameter",
        value_name="Init_value",
    )
    df.insert(loc=len(cols) + 1, column="Date", value=zero_time)
    return df


def _add_param_bounds(
    df: pd.DataFrame, mmb_config: MmbSettings
) -> pd.DataFrame:
    for param in mmb_config.params:
        crit = df["Parameter"].isin(param.symbols)
        df.loc[crit, "Min_value"] = param.min_value
        df.loc[crit, "Max_value"] = param.max_value
    return df


def _get_params(descr: pd.DataFrame, zero_time: date) -> pd.DataFrame:
    df = _prepare_params(descr)
    df = _unstack_params(df, zero_time)
    return df


def _build_params(
    descr: pd.DataFrame,
    zero_time: date,
    to_tank: pd.Series,
    mmb_config: MmbSettings,
) -> pd.DataFrame:
    connections = _get_connections(descr, to_tank, zero_time)
    params = _get_params(descr, zero_time)
    params = pd.concat([connections, params])
    params = _add_param_bounds(params, mmb_config)
    params = params.assign(alpha=None)
    params["Neighb"] = params["Neighb"].fillna("")
    return params


async def _rate_task(
    path: Path,
    descr: pd.DataFrame,
    uids: pd.DataFrame,
    hist: dict[str, pd.DataFrame],
    pool: ProcessPoolManager,
    csv_config: CsvSettings,
    zero_time: date,
    to_tank: pd.Series,
    mmb_config: MmbSettings,
) -> None:
    df = await pool.run(
        _calc_rates, descr, uids, hist, to_tank, zero_time, mmb_config
    )
    await save_to_csv(
        df,
        path / "tank_prod.csv",
        csv_config.encoding,
        csv_config.delimiter,
    )


async def _param_task(
    path: Path,
    descr: pd.DataFrame,
    pool: ProcessPoolManager,
    csv_config: CsvSettings,
    zero_time: date,
    to_tank: pd.Series,
    mmb_config: MmbSettings,
) -> None:
    df = await pool.run(_build_params, descr, zero_time, to_tank, mmb_config)
    await save_to_csv(
        df,
        path / "tank_params.csv",
        csv_config.encoding,
        csv_config.delimiter,
    )


async def mmb_report(
    path: Path,
    alternative: bool,
    dao: MmbReporter,
    pool: ProcessPoolManager,
    delimiter: str,
    csv_config: CsvSettings,
    mmb_config: MmbSettings,
) -> None:
    descr = await dao.get_description()
    uids = _get_uids(descr, delimiter)
    uid_list = uids.agg("".join, axis=1).to_list()
    hist = await dao.get_history(uid_list, alternative)
    zero_time = _get_zero_time(hist["rates"])
    to_tank = _tank_mapping(descr)
    async with asyncio.TaskGroup() as tg:
        tg.create_task(
            _rate_task(
                path,
                descr,
                uids,
                hist,
                pool,
                csv_config,
                zero_time,
                to_tank,
                mmb_config,
            )
        )
        tg.create_task(
            _param_task(
                path,
                descr,
                pool,
                csv_config,
                zero_time,
                to_tank,
                mmb_config,
            )
        )
    make_archive(str(path), "zip", root_dir=path)
