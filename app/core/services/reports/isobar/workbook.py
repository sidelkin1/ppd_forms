"""Запись книги: формулы шаблона, строки и сохранение."""

import time
from copy import copy
from datetime import date
from pathlib import Path
from typing import Any, cast

import openpyxl
import pandas as pd
from openpyxl.formula.translate import Translator
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.writer.excel import save_workbook

from .columns import (
    COL_STATUS,
    DATE_COLUMNS,
    DATE_FORMAT,
    FIRST_ROW,
    LAST_COLUMN,
    REQUIRED_FORMULA_COLUMNS,
    SHEET,
    SKIP_FORMULA_COLUMNS,
    SYNTHETIC_STATUS_COLORS,
    VALUE_COLUMNS,
)
from .diagnostics import write_diagnostics
from .preparation import prepare_dataframe, prepare_tests


def _template_formulas(ws: Worksheet) -> dict[int, str]:
    """Формулы из строки-образца шаблона: номер колонки → формула.

    Колонки I и AH (показатели, которые считаются вручную) пропускаются.
    Проверяет, что обязательные формулы A, B, H на месте.
    """
    formulas: dict[int, str] = {}
    for column in range(1, LAST_COLUMN + 1):
        value = ws.cell(FIRST_ROW, column).value
        if not isinstance(value, str) or not value.startswith("="):
            continue
        if column in SKIP_FORMULA_COLUMNS:
            continue
        formulas[column] = value
    missing = [
        column for column in REQUIRED_FORMULA_COLUMNS if column not in formulas
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
    """Пустое значение в колонке: None, NaN или NaT."""
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _copy_styles(ws: Worksheet, row_number: int, styles: list[Any]) -> None:
    """Копирует оформление образцовой строки на новую строку."""
    for column in range(1, LAST_COLUMN + 1):
        cell = cast(Any, ws.cell(row_number, column))
        cell._style = styles[column - 1]


def _mark_synthetic_status(cell: Any, color: str) -> None:
    """Синтетическое состояние: скобки, курсив и свой цвет.

    Так «стар. ствол» и «открыт. перф.» (состояния, которых нет в
    справочнике) видно на фоне обычных состояний скважины. Шрифт
    копируется целиком: подчёркивание и прочее оформление шаблона
    сохраняются.
    """
    font = copy(cell.font)
    font.italic = True
    font.color = color
    cell.font = font
    cell.value = f"[{cell.value}]"


def _write_row(
    ws: Worksheet,
    row_number: int,
    row: Any,
    translators: dict[int, Translator],
) -> None:
    """Пишет строку отчёта: значения по колонкам и копии формул."""
    for column in range(1, LAST_COLUMN + 1):
        ws.cell(row_number, column).value = None
    for column, name in VALUE_COLUMNS.items():
        value = getattr(row, name)
        if _is_empty(value):
            continue
        cell = ws.cell(row_number, column)
        cell.value = value
        if column in DATE_COLUMNS:
            cell.number_format = DATE_FORMAT
    color = SYNTHETIC_STATUS_COLORS.get(str(row.status))
    if color is not None:
        _mark_synthetic_status(ws.cell(row_number, COL_STATUS), color)
    for column, translator in translators.items():
        letter = get_column_letter(column)
        ws.cell(row_number, column).value = translator.translate_formula(
            f"{letter}{row_number}"
        )


def _fill_workbook(
    df: pd.DataFrame, template: Path, target: Path
) -> dict[str, float]:
    """Заполняет копию шаблона строками отчёта и сохраняет её.

    Выполняется в отдельном процессе. Лишние строки образца удаляются,
    недостающие получают оформление образцовой строки. Возвращает
    тайминги по этапам.
    """
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


def process_workbook(
    dfs: dict[str, pd.DataFrame],
    on_date: date,
    template: Path,
    target: Path,
) -> dict[str, Any]:
    """Пишет диагностику и книгу отчёта.

    Выполняется в отдельном процессе: возвращает тайминги, статистику и
    готовые сообщения диагностики — их в лог пишет сервис.
    """
    start = time.perf_counter()
    dfs, fallbacks = prepare_tests(dfs)
    diagnostics = write_diagnostics(
        path=target.parent,
        on_date=on_date,
        dfs=dfs,
        fallbacks=fallbacks,
    )
    df = prepare_dataframe(dfs)
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
    return {"timings": timings, "stats": stats, "diagnostics": diagnostics}
