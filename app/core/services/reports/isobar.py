import logging
import re
import time
from copy import copy
from datetime import date
from pathlib import Path
from shutil import make_archive
from typing import Any, cast

import openpyxl
import pandas as pd
from openpyxl.formula.translate import Translator
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.writer.excel import save_workbook

from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.dao.complex.reporters import IsobarReporter

logger = logging.getLogger(__name__)

SHEET = "текущие отборы"
FIRST_ROW = 2
LAST_COLUMN = 54  # BB

_COL_FIELD = 3  # C
_COL_RESERVOIR = 4  # D
_COL_WELL = 5  # E
_COL_TYPE = 6  # F
_COL_STATUS = 7  # G
_COL_PRESSURE_GDI = 8  # H (формула)
_COL_BHP = 9  # I
_COL_PREV_RESP = 10  # J
_COL_PREV_DATE = 11  # K
_COL_PREV_TEST = 12  # L
_COL_PREV_TYPE = 13  # M
_COL_PREV_STATUS = 14  # N
_COL_RESP = 15  # O
_COL_DATE = 16  # P
_COL_WELL_TEST = 17  # Q
_COL_FAILED_RESP = 29  # AC
_COL_FAILED_DATE = 30  # AD
_COL_FAILED_TEST = 31  # AE
_COL_BUBBLE = 34  # AH

_DATE_COLUMNS = (_COL_PREV_DATE, _COL_DATE, _COL_FAILED_DATE)
_DATE_FORMAT = "DD.MM.YYYY"
_OUTPUT_PREFIX = "СВОДНЫЙ_ИЗОБАРЫ"
_MISS_HEADERS = {
    "field": "Месторождение",
    "well_name": "Скважина",
    "cid": "Объект в фонде",
    "file_reservoir": "Объекты в предыдущей сводной",
}
_STATE_HEADERS = {
    "field": "Месторождение",
    "well": "Скважина",
    "end_date": "Дата замера",
    "reservoir": "Объект",
    "well_test": "Вид исследования",
    "resp": "Рпл",
}
_LOST_HEADERS = {
    "field": "Месторождение",
    "well": "Скважина",
    "reservoir": "Объект",
    "well_test": "Вид исследования",
    "resp": "Рпл",
    "end_date": "Дата",
}

_VALUE_COLUMNS = {
    _COL_FIELD: "field",
    _COL_RESERVOIR: "reservoir",
    _COL_WELL: "well_name",
    _COL_TYPE: "type_",
    _COL_STATUS: "status",
    _COL_BHP: "p_bhp",
    _COL_PREV_RESP: "prev_resp",
    _COL_PREV_DATE: "prev_date",
    _COL_PREV_TEST: "prev_well_test",
    _COL_PREV_TYPE: "state_type",
    _COL_PREV_STATUS: "state_status",
    _COL_RESP: "current_resp",
    _COL_DATE: "current_date",
    _COL_WELL_TEST: "current_well_test",
    _COL_FAILED_RESP: "failed_resp_owc",
    _COL_FAILED_DATE: "failed_end_date",
    _COL_FAILED_TEST: "failed_well_test",
    _COL_BUBBLE: "p_bubble",
}
_SKIP_FORMULA_COLUMNS = (_COL_BHP, _COL_BUBBLE)
_REQUIRED_FORMULA_COLUMNS = (1, 2, _COL_PRESSURE_GDI)  # A, B, H


def _natural_key(value: Any) -> tuple[Any, ...]:
    return tuple(
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", str(value))
    )


def _to_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce").dt.date


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


def _previous_misses(
    df: pd.DataFrame, prev_values: pd.DataFrame
) -> pd.DataFrame:
    """Объекты фонда, для которых в предыдущей сводной нет строки."""
    columns = ["field", "well_name", "cid", "file_reservoir"]
    if prev_values.empty:
        return pd.DataFrame(columns=columns)
    file_keys = prev_values[["field", "well", "reservoir"]].drop_duplicates()
    file_wells = file_keys[["field", "well"]].drop_duplicates()
    stock_keys = df[["field", "well_name", "cid"]].drop_duplicates()
    candidates = stock_keys.merge(
        file_wells,
        left_on=["field", "well_name"],
        right_on=["field", "well"],
    )
    check = candidates.merge(
        file_keys,
        left_on=["field", "well_name", "cid"],
        right_on=["field", "well", "reservoir"],
        how="left",
        indicator=True,
    )
    missed = check[check["_merge"] == "left_only"].drop_duplicates(
        subset=["field", "well_name", "cid"]
    )
    file_by_well = (
        file_keys.groupby(["field", "well"])["reservoir"]
        .agg(lambda values: ", ".join(sorted(map(str, values))))
        .to_dict()
    )
    missed = missed.assign(
        file_reservoir=[
            file_by_well.get((field, well), "")
            for field, well in zip(missed["field"], missed["well_name"])
        ]
    )
    return missed[columns].reset_index(drop=True)


def _write_misses(missed: pd.DataFrame, target: Path) -> str:
    """Пишет объекты фонда без строки в сводной, возвращает имя файла."""
    path = target.with_name(f"{target.stem}_нет_строки_в_сводной.csv")
    missed.rename(columns=_MISS_HEADERS).to_csv(
        path, index=False, sep=";", encoding="utf-8-sig"
    )
    return path.name


def _write_state_misses(
    path: Path, on_date: date, missing: pd.DataFrame | None
) -> None:
    """Пишет ключи предыдущей сводной без записей в welltest."""
    if missing is None or missing.empty:
        return
    name = f"{_OUTPUT_PREFIX}_{on_date:%d.%m.%Y}_нет_данных_гдис.csv"
    missing.rename(columns=_STATE_HEADERS).to_csv(
        path / name, index=False, sep=";", encoding="utf-8-sig"
    )
    logger.warning(
        "Изобары: для %d ключей предыдущей сводной нет записей в "
        "welltest (M/N не заполнены) — полный список в файле «%s»",
        len(missing),
        name,
    )


def _write_lost_values(
    path: Path,
    on_date: date,
    missing: pd.DataFrame | None,
    suffix: str,
    source: str,
) -> None:
    """Пишет Рпл из источника, которому не нашлось пары в фонде."""
    if missing is None or missing.empty:
        return
    name = f"{_OUTPUT_PREFIX}_{on_date:%d.%m.%Y}_{suffix}.csv"
    missing.rename(columns=_LOST_HEADERS).to_csv(
        path / name, index=False, sep=";", encoding="utf-8-sig"
    )
    logger.warning(
        "Изобары: %d строк %s с Рпл не попали в фонд — полный список в "
        "файле «%s»",
        len(missing),
        source,
        name,
    )


def _prepare_dataframe(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Сводит фонд, текущие замеры, предыдущие значения и M/N."""
    stock = dfs["stock"].copy()
    if stock.empty:
        raise ValueError("Не удалось получить текущий фонд скважин")

    succeeded = dfs["succeeded"].rename(
        columns={
            "well": "test_well",
            "reservoir": "test_reservoir",
            "well_test": "test_well_test",
            "end_date": "test_end_date",
            "resp_owc": "test_resp_owc",
        }
    )
    failed = dfs["failed"].rename(
        columns={
            "well": "failed_well",
            "reservoir": "failed_reservoir",
            "well_test": "failed_well_test",
            "end_date": "failed_end_date",
            "resp_owc": "failed_resp_owc",
        }
    )

    df = stock.merge(
        succeeded,
        left_on=["field", "parent", "cid"],
        right_on=["field", "test_well", "test_reservoir"],
        how="left",
        validate="many_to_one",
    )
    df = df.merge(
        failed,
        left_on=["field", "parent", "cid"],
        right_on=["field", "failed_well", "failed_reservoir"],
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
    df["prev_date"] = _to_date(df["prev_date"])
    df["test_end_date"] = _to_date(df["test_end_date"])
    df["failed_end_date"] = _to_date(df["failed_end_date"])

    state = dfs["prev_state"]
    if state.empty:
        df["state_type"] = None
        df["state_status"] = None
    else:
        state = state.copy()
        state["end_date"] = _to_date(state["end_date"])
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
    unique = df.drop_duplicates(subset=["field", "well_name", "reservoir"])
    if len(unique) != len(df):
        logger.warning("Дубли скважин в фонде: %d", len(df) - len(unique))
    return unique.reset_index(drop=True)


def _template_formulas(ws: Worksheet) -> dict[int, str]:
    formulas: dict[int, str] = {}
    for column in range(1, LAST_COLUMN + 1):
        value = ws.cell(FIRST_ROW, column).value
        if not isinstance(value, str) or not value.startswith("="):
            continue
        if column in _SKIP_FORMULA_COLUMNS:
            continue
        formulas[column] = value
    missing = [
        column
        for column in _REQUIRED_FORMULA_COLUMNS
        if column not in formulas
    ]
    if missing:
        letters = ", ".join(
            get_column_letter(column) for column in sorted(missing)
        )
        raise ValueError(
            f"В строке 2 шаблона нет формул в колонках: {letters}"
        )
    return formulas


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _copy_styles(ws: Worksheet, row_number: int, styles: list[Any]) -> None:
    for column in range(1, LAST_COLUMN + 1):
        cell = cast(Any, ws.cell(row_number, column))
        cell._style = styles[column - 1]


def _write_row(
    ws: Worksheet,
    row_number: int,
    row: Any,
    translators: dict[int, Translator],
) -> None:
    for column in range(1, LAST_COLUMN + 1):
        ws.cell(row_number, column).value = None
    for column, name in _VALUE_COLUMNS.items():
        value = getattr(row, name, None)
        if _is_empty(value):
            continue
        cell = ws.cell(row_number, column)
        cell.value = value
        if column in _DATE_COLUMNS:
            cell.number_format = _DATE_FORMAT
    for column, translator in translators.items():
        letter = get_column_letter(column)
        ws.cell(row_number, column).value = translator.translate_formula(
            f"{letter}{row_number}"
        )


def _fill_workbook(
    df: pd.DataFrame, template: Path, target: Path
) -> dict[str, float]:
    timings: dict[str, float] = {}
    start = time.perf_counter()
    wb = openpyxl.load_workbook(template, keep_vba=True)
    timings["time_load"] = round(time.perf_counter() - start, 1)
    try:
        if SHEET not in wb.sheetnames:
            raise ValueError(f"В файле отсутствует лист «{SHEET}»")
        ws = wb[SHEET]
        translators = {
            column: Translator(
                formula, f"{get_column_letter(column)}{FIRST_ROW}"
            )
            for column, formula in _template_formulas(ws).items()
        }
        styles = [
            copy(cast(Any, ws.cell(FIRST_ROW, column))._style)
            for column in range(1, LAST_COLUMN + 1)
        ]
        last_template_row = ws.max_row
        old_count = max(last_template_row - FIRST_ROW + 1, 0)
        start = time.perf_counter()
        for index, row in enumerate(df.itertuples(index=False)):
            row_number = FIRST_ROW + index
            if row_number > last_template_row:
                _copy_styles(ws, row_number, styles)
            _write_row(ws, row_number, row, translators)
        timings["time_write"] = round(time.perf_counter() - start, 1)
        new_count = len(df)
        if new_count < old_count:
            start = time.perf_counter()
            ws.delete_rows(FIRST_ROW + new_count, old_count - new_count)
            timings["time_delete"] = round(time.perf_counter() - start, 1)
        start = time.perf_counter()
        save_workbook(wb, target)
        timings["time_save"] = round(time.perf_counter() - start, 1)
    finally:
        wb.close()
    return timings


def _process_workbook(
    dfs: dict[str, pd.DataFrame], template: Path, target: Path
) -> dict[str, Any]:
    start = time.perf_counter()
    df = _prepare_dataframe(dfs)
    prepare = time.perf_counter() - start
    stats: dict[str, int] = {
        "rows_stock": len(df),
        # счётчики по заполненным ячейкам отчёта: J, O, AC, M/N
        "rows_previous": int(df["prev_resp"].notna().sum()),
        "rows_current": int(df["current_resp"].notna().sum()),
        "rows_failed": int(df["failed_resp_owc"].notna().sum()),
        "rows_previous_state": int(df["state_type"].notna().sum()),
    }
    timings: dict[str, float] = {
        "time_prepare": round(prepare, 1),
        **_fill_workbook(df, template, target),
    }
    result: dict[str, Any] = {"timings": timings, "stats": stats}
    missed = _previous_misses(df, dfs["prev_values"])
    if not missed.empty:
        result["prev_missed"] = len(missed)
        result["prev_missed_file"] = _write_misses(missed, target)
    return result


async def isobar_report(
    path: Path,
    template: Path,
    previous_date: date,
    on_date: date,
    stock_date: date,
    dao: IsobarReporter,
    pool: ProcessPoolManager,
) -> None:
    start = time.perf_counter()
    dfs = await dao.read_all(
        stock_date=stock_date,
        on_date=on_date,
        previous_date=previous_date,
    )
    read = time.perf_counter() - start
    _write_state_misses(path, on_date, dfs.get("prev_missing"))
    _write_lost_values(
        path,
        on_date,
        dfs.get("prev_unmatched"),
        "нет_в_фонде_сводная",
        "предыдущей сводной",
    )
    _write_lost_values(
        path,
        on_date,
        dfs.get("test_unmatched"),
        "нет_в_фонде_welltest",
        "текущих замеров",
    )
    target = path / f"{_OUTPUT_PREFIX}_{on_date:%d.%m.%Y}.xlsm"
    start = time.perf_counter()
    result = await pool.run(_process_workbook, dfs, template, target)
    worker = time.perf_counter() - start
    start = time.perf_counter()
    make_archive(str(path), "zip", root_dir=path)
    archive = time.perf_counter() - start
    logger.info(
        "Изобары, тайминги",
        extra={
            "time_read": round(read, 1),
            "time_worker": round(worker, 1),
            "time_zip": round(archive, 1),
            **result["timings"],
        },
    )
    logger.info("Изобары, статистика", extra=result["stats"])
    if result.get("prev_missed"):
        logger.warning(
            "Изобары: для %d объектов фонда нет строки в предыдущей "
            "сводной — полный список в файле «%s»",
            result["prev_missed"],
            result.get("prev_missed_file"),
        )
