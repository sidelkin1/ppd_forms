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

_EXCEL_NEIGHBS_START_ROW = 2
_EXCEL_NEIGHBS_START_COLUMN = 22
_EXCEL_NEIGHBS_LAST_COLUMN = 29


def _get_uids(neighbs: pd.DataFrame) -> list[str]:
    if neighbs.empty:
        return []
    cols = ["field", "well", "reservoir"]
    return neighbs[cols].agg("".join, axis=1).to_list()


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


def _add_distance(tests: pd.DataFrame, neighbs: pd.DataFrame) -> pd.DataFrame:
    cols = ["field", "well", "reservoir"]
    return pd.merge(tests, neighbs, on=cols, how="left").sort_values(
        ["reservoir", "distance"]
    )


def _process_data(
    results: list[WellTestResult],
    gtms: pd.DataFrame,
    tests: pd.DataFrame,
    neighbs: pd.DataFrame,
    neighb_tests: pd.DataFrame,
    path: Path,
    template: Path,
) -> None:
    result = path / template.name
    tests = _concat_tests(tests, results)
    neighb_tests = _add_distance(neighb_tests, neighbs)
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
        _fill_template(
            ws,
            neighb_tests,
            _EXCEL_NEIGHBS_START_ROW,
            _EXCEL_NEIGHBS_START_COLUMN,
            _EXCEL_NEIGHBS_LAST_COLUMN,
        )
        save_workbook(wb, result)
    finally:
        wb.close()


async def well_test_report(
    path: Path,
    template: Path,
    gtm_period: int,
    gdis_period: int,
    radius: float,
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
    neighbs = await dao.get_neighbs(
        results[0]["field"], results[0]["well"], reservoirs, radius
    )
    uids = _get_uids(neighbs)
    date_from = results[0]["end_date"].replace(day=1) - relativedelta(
        years=gdis_period
    )
    neighb_tests = await dao.get_neighb_tests(
        uids, date_from, results[0]["end_date"]
    )
    await pool.run(
        _process_data,
        results,
        gtms,
        tests,
        neighbs,
        neighb_tests,
        path,
        template,
    )
    make_archive(str(path), "zip", root_dir=path)
