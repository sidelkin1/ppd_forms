from pathlib import Path
from shutil import make_archive

import openpyxl
import pandas as pd
from dateutil.relativedelta import relativedelta
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.writer.excel import save_workbook

from app.core.models.dto import WellTestResult
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.dao.complex.reporters import WellTestReporter

_EXCEL_GDIS_START_ROW = 2
_EXCEL_GDIS_START_COLUMN = 1
_EXCEL_GDIS_LAST_COLUMN = 12

_EXCEL_GTM_START_ROW = 2
_EXCEL_GTM_START_COLUMN = 14
_EXCEL_GTM_LAST_COLUMN = 20


def _fill_template(
    ws: Worksheet, df: pd.DataFrame, min_row: int, min_col: int, max_col: int
) -> None:
    for row, df_row in zip(
        ws.iter_rows(
            min_row=min_row,
            min_col=min_col,
            max_col=max_col,
            max_row=df.shape[0] + min_row - 1,
        ),
        df.itertuples(index=False),
    ):
        for cell, value in zip(row, df_row):
            cell.value = value


def _concat_tests(
    tests: pd.DataFrame, results: list[WellTestResult]
) -> pd.DataFrame:
    df = pd.DataFrame(results, columns=tests.columns)
    return df if tests.empty else pd.concat([tests, df], ignore_index=True)


def _process_data(
    results: list[WellTestResult],
    gtms: pd.DataFrame,
    tests: pd.DataFrame,
    path: Path,
    template: Path,
) -> None:
    result = path / template.name
    tests = _concat_tests(tests, results)
    try:
        wb = openpyxl.load_workbook(template)
        ws = wb["Лист1"]
        start_row = _EXCEL_GDIS_START_ROW
        for _, df in tests.groupby("reservoir"):
            _fill_template(
                ws,
                df,
                start_row,
                _EXCEL_GDIS_START_COLUMN,
                _EXCEL_GDIS_LAST_COLUMN,
            )
            start_row += df.shape[0]
        _fill_template(
            ws,
            gtms,
            _EXCEL_GTM_START_ROW,
            _EXCEL_GTM_START_COLUMN,
            _EXCEL_GTM_LAST_COLUMN,
        )
        save_workbook(wb, result)
    finally:
        wb.close()


async def well_test_report(
    path: Path,
    template: Path,
    gtm_period: int,
    dao: WellTestReporter,
    pool: ProcessPoolManager,
) -> None:
    results = await dao.get_results()
    date_from = results[0]["end_date"].replace(day=1) - relativedelta(
        months=gtm_period
    )
    reservoirs = [result["reservoir"] for result in results]
    gtms = await dao.get_well_gtms(
        results[0]["field"],
        results[0]["well"],
        date_from,
        results[0]["end_date"],
    )
    tests = await dao.get_well_tests(
        results[0]["field"],
        results[0]["well"],
        reservoirs,
        results[0]["end_date"],
    )
    await pool.run(_process_data, results, gtms, tests, path, template)
    make_archive(str(path), "zip", root_dir=path)
