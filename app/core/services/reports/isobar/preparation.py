"""Подготовка строк отчёта: фонд, текущие замеры, предыдущая сводная."""

import re
from typing import Any

import pandas as pd

from .columns import LOST_COLUMNS


def _natural_key(value: Any) -> tuple[Any, ...]:
    """Ключ сортировки, где числа сравниваются как числа: «10» после «9»."""
    return tuple(
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", str(value))
    )


def _use_db_value(db_date: pd.Series, prev_date: pd.Series) -> pd.Series:
    """Брать замер из БД, если он не старше значения из предыдущей сводной."""
    return db_date.notna() & (prev_date.isna() | (db_date >= prev_date))


def _fill_current_measurements(df: pd.DataFrame) -> pd.DataFrame:
    """O-Q: квартальный замер обновляет перенесённые старые значения."""
    use_db = _use_db_value(df["test_end_date"], df["prev_date"])
    df["current_resp"] = df["test_resp_owc"].where(use_db, df["prev_resp"])
    df["current_date"] = df["test_end_date"].where(use_db, df["prev_date"])
    df["current_well_test"] = df["test_well_test"].where(
        use_db, df["prev_well_test"]
    )
    return df


def _resolve_branches(
    tests: pd.DataFrame, perfs: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Стволы, открытые на дату замера: замер идёт в каждый из них.

    Перфорации приходят по ключу (месторождение, скважина без ствола,
    объект). Замер привязывается ко **всем** стволам, у которых на его
    дату открыт интервал перфорации, поэтому строк замера может стать
    больше. Если открытых стволов нет — остаётся номер скважины без
    ствола (как он пришёл из welltest), а замер попадает во второй
    список — для диагностики.
    """
    if tests.empty:
        return (
            tests.assign(branch=pd.Series(dtype=object)),
            pd.DataFrame(columns=list(LOST_COLUMNS)),
        )
    if perfs.empty:
        return (
            tests.assign(branch=tests["well"]),
            _fallback_frame(tests),
        )

    tests = tests.reset_index(drop=True)
    tests["_row"] = range(len(tests))
    tests["_date"] = pd.to_datetime(tests["end_date"], errors="coerce")
    intervals = pd.DataFrame(
        {
            "field": perfs["field"],
            "well": perfs["well"],
            "reservoir": perfs["reservoir"],
            "branch": perfs["branch"].astype(str),
            "_comp": pd.to_datetime(perfs["comp_date"], errors="coerce"),
            "_close": pd.to_datetime(perfs["close_date"], errors="coerce"),
        }
    )
    merged = tests.merge(
        intervals, on=["field", "well", "reservoir"], how="left"
    )
    covered = merged[
        merged["_comp"].notna()
        & (merged["_comp"] <= merged["_date"])
        & (merged["_close"].isna() | (merged["_close"] >= merged["_date"]))
    ]
    # замеры без открытых стволов: одна строка на замер, ствол — скважина
    without_open = merged[~merged["_row"].isin(covered["_row"])]
    fallback = without_open.drop_duplicates("_row")
    resolved = (
        pd.concat(
            [
                covered,
                fallback.assign(branch=fallback["well"].astype(str)),
            ]
        )
        .drop(columns=["_date", "_comp", "_close"])
        .drop_duplicates(["_row", "branch"])
        .sort_values(["_row", "branch"])
        .drop(columns=["_row"])
        .reset_index(drop=True)
    )
    return resolved, _fallback_frame(fallback)


def _fallback_frame(tests: pd.DataFrame) -> pd.DataFrame:
    """Список замеров, для которых не нашлось открытой перфорации."""
    return pd.DataFrame(
        {
            "field": tests["field"],
            "well": tests["well"],
            "reservoir": tests["reservoir"],
            "well_test": tests["well_test"],
            "resp": tests["resp_owc"].round(2),
            "end_date": tests["end_date"],
        }
    ).reset_index(drop=True)


def to_date(series: pd.Series) -> pd.Series:
    """Приводит колонку к датам; нераспознанные значения — None."""
    return pd.to_datetime(series, errors="coerce").dt.date


def prepare_tests(
    dfs: dict[str, pd.DataFrame],
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Привязывает замеры к стволам, открытым на их дату.

    Меняет ``dfs`` на месте: в ``succeeded``/``failed`` появляется колонка
    ``branch``; возвращается тот же словарь. Второй элемент — общий список
    замеров, для которых открытой перфорации не нашлось.
    """
    perfs = dfs["perfs"]
    dfs["succeeded"], fallback_succeeded = _resolve_branches(
        dfs["succeeded"], perfs
    )
    dfs["failed"], fallback_failed = _resolve_branches(dfs["failed"], perfs)
    fallbacks = pd.concat(
        [fallback_succeeded, fallback_failed], ignore_index=True
    )
    return dfs, fallbacks


def prepare_dataframe(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Сводит фонд с квартальными замерами, предыдущей сводной и M/N.

    По строке на ствол фонда: прошлые значения (J-N), текущий замер (O-Q)
    и неуспешные замеры (AC-AE).
    """
    stock = dfs["stock"].copy()
    if stock.empty:
        raise ValueError("Не удалось получить текущий фонд скважин")

    # оценка замера (curator) нужна только диагностике, в сводную не идёт
    succeeded = (
        dfs["succeeded"]
        .drop(columns=["curator"])
        .rename(
            columns={
                "well": "test_well",
                "reservoir": "test_reservoir",
                "branch": "test_branch",
                "well_test": "test_well_test",
                "end_date": "test_end_date",
                "resp_owc": "test_resp_owc",
            }
        )
    )
    failed = (
        dfs["failed"]
        .drop(columns=["curator"])
        .rename(
            columns={
                "well": "failed_well",
                "reservoir": "failed_reservoir",
                "branch": "failed_branch",
                "well_test": "failed_well_test",
                "end_date": "failed_end_date",
                "resp_owc": "failed_resp_owc",
            }
        )
    )

    # Замер привязан к стволу, работавшему на его дату; фонд хранит ствол
    # в well_name, поэтому ключ склейки — (месторождение, объект, ствол).
    df = stock.merge(
        succeeded,
        left_on=["field", "well_name", "cid"],
        right_on=["field", "test_branch", "test_reservoir"],
        how="left",
        validate="many_to_one",
    )
    df = df.merge(
        failed,
        left_on=["field", "well_name", "cid"],
        right_on=["field", "failed_branch", "failed_reservoir"],
        how="left",
        validate="many_to_one",
    )
    # Ключ склейки с предыдущей сводной — cid: локальное имя объекта
    # (sdes без суффикса «(Руд)»). В файле после reservoir_mapper лежит
    # ровно такое же локальное имя, поэтому домены совпадают.
    df = df.merge(
        dfs["prev_values"],
        left_on=["field", "well_name", "cid"],
        right_on=["field", "well", "reservoir"],
        how="left",
        validate="many_to_one",
        suffixes=("", "_prev"),
    )
    df["prev_date"] = to_date(df["prev_date"])
    df["test_end_date"] = to_date(df["test_end_date"])
    df["failed_end_date"] = to_date(df["failed_end_date"])

    state = dfs["prev_state"]
    if state.empty:
        df["state_type"] = None
        df["state_status"] = None
    else:
        state = state.copy()
        state["end_date"] = to_date(state["end_date"])
        state = state.drop_duplicates(
            subset=["field", "well", "end_date", "reservoir"], keep="first"
        ).rename(
            columns={
                "well": "state_well",
                "end_date": "state_end_date",
                "reservoir": "state_reservoir",
                "well_type": "state_type",
                "well_status": "state_status",
            }
        )
        df = df.merge(
            state,
            left_on=["field", "parent", "prev_date", "cid"],
            right_on=[
                "field",
                "state_well",
                "state_end_date",
                "state_reservoir",
            ],
            how="left",
            validate="many_to_one",
        )

    df = _fill_current_measurements(df)
    df = df.sort_values(
        ["field", "reservoir", "well_name"],
        key=lambda series: series.map(_natural_key),
    )
    return df.reset_index(drop=True)
