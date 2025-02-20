from copy import copy, deepcopy
from datetime import date
from io import BytesIO
from pathlib import Path
from shutil import make_archive
from typing import cast

import openpyxl
import pandas as pd
from dateutil.relativedelta import relativedelta
from openpyxl.drawing.image import Image
from openpyxl.drawing.spreadsheet_drawing import TwoCellAnchor
from openpyxl.styles import Border, Side
from openpyxl.utils import quote_sheetname
from openpyxl.utils.datetime import to_excel
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.writer.excel import save_workbook
from PIL import Image as PILImage
from PIL import ImageOps

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

_REPORT_SHEET_NAME = "отчет"

_REPORT_ISOBARS_ANCHOR = "B13"
_REPORT_ISOBARS_WIDTH_MM = 110.0
_REPORT_ISOBARS_HEIGHT_MM = 110.0
_REPORT_ISOBARS_DPI = 96
_REPORT_ISOBARS_WIDTH_PX = int(
    round(_REPORT_ISOBARS_WIDTH_MM * _REPORT_ISOBARS_DPI / 25.4)
)
_REPORT_ISOBARS_HEIGHT_PX = int(
    round(_REPORT_ISOBARS_HEIGHT_MM * _REPORT_ISOBARS_DPI / 25.4)
)

_REPORT_CELL_TITLE = "B3"
_REPORT_CELL_DATE = "E5"
_REPORT_CELL_RESERVOIR = "E6"
_REPORT_CELL_PURPOSE = "E7"
_REPORT_CELL_CONCLUSION = "B9"
_REPORT_CELL_TEST_WELL = "B11"
_REPORT_CELL_TEST_NAME = "C11"
_REPORT_CELL_TEST_DATE = "D11"
_REPORT_CELL_TEST_PRESSURE = "E11"
_REPORT_CELL_TEST_PERMEABILITY = "F11"
_REPORT_CELL_TEST_SKIN_FACTOR = "G11"
_REPORT_CELL_TEST_PROD_INDEX = "H11"
_REPORT_CELL_TEST_FRAC_LENGTH = "I11"
_REPORT_CELL_TEST_RELIABILITY = "J11"

_REPORT_CHART_ANCHOR = "F12"
_REPORT_CHART_HEIGHT = 22
_REPORT_CHART_WIDTH = 4
_REPORT_CHART_INDEX = 0
_REPORT_FOOTER_ANCHOR = "H35"
_REPORT_FOOTER_INDEX = 3


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


def _resize_isobars(isobars: Image) -> Image:
    image_stream = cast(BytesIO, isobars.ref)
    image_stream.seek(0)
    with PILImage.open(image_stream) as pil_image:
        pil_image.load()
        resized_image = ImageOps.fit(
            pil_image,
            (_REPORT_ISOBARS_WIDTH_PX, _REPORT_ISOBARS_HEIGHT_PX),
        )
    output_stream = BytesIO()
    resized_image.save(output_stream, format=isobars.format)
    output_stream.seek(0)
    return Image(output_stream)


def _fill_data_sheet(
    wb: openpyxl.Workbook,
    gtms: pd.DataFrame,
    tests: pd.DataFrame,
    neighb_tests: pd.DataFrame,
) -> None:
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


def _copy_sheets(
    wb: openpyxl.Workbook, reservoirs: list[str]
) -> list[Worksheet]:
    ws = wb[_REPORT_SHEET_NAME]
    if len(reservoirs) == 1:
        return [ws]
    sheets = []
    for reservoir in reservoirs:
        copy_ws = wb.copy_worksheet(ws)
        copy_ws.title = f"{_REPORT_SHEET_NAME} ({reservoir})"
        copy_ws.views = copy(ws.views)
        copy_ws._images = deepcopy(ws._images)  # type: ignore[attr-defined]
        copy_ws._charts = deepcopy(ws._charts)  # type: ignore[attr-defined]
        copy_ws.sheet_view.tabSelected = False
        sheets.append(copy_ws)
    wb.remove(ws)
    return sheets


def _fill_test_history(ws: Worksheet, tests: pd.DataFrame) -> None:
    border = Border(
        left=Side(border_style="thin", color="00000000"),
        right=Side(border_style="thin", color="00000000"),
        top=Side(border_style="thin", color="00000000"),
        bottom=Side(border_style="thin", color="00000000"),
    )
    coords = (
        {"cell": _REPORT_CELL_TEST_WELL, "source": "well"},
        {"cell": _REPORT_CELL_TEST_NAME, "source": "well_test"},
        {"cell": _REPORT_CELL_TEST_DATE, "source": "end_date"},
        {"cell": _REPORT_CELL_TEST_PRESSURE, "source": "resp_owc"},
        {"cell": _REPORT_CELL_TEST_PERMEABILITY, "source": "permeability"},
        {"cell": _REPORT_CELL_TEST_SKIN_FACTOR, "source": "skin_factor"},
        {"cell": _REPORT_CELL_TEST_PROD_INDEX, "source": "prod_index"},
        {"cell": _REPORT_CELL_TEST_FRAC_LENGTH, "source": "frac_length"},
        {"cell": _REPORT_CELL_TEST_RELIABILITY, "source": "reliability"},
    )
    for row_num, df_row in enumerate(tests.itertuples(index=False)):
        for coord in coords:
            cell = ws[coord["cell"]].offset(row=row_num)
            cell.value = getattr(df_row, coord["source"])
            cell.border = border


def _shift_drawings(ws: Worksheet, nrow: int) -> None:
    chart = ws._charts[_REPORT_CHART_INDEX]  # type: ignore[attr-defined]
    cell = ws[_REPORT_CHART_ANCHOR].offset(nrow - 1)
    anchor = TwoCellAnchor()
    anchor._from.col = cell.column  # type: ignore[union-attr]
    anchor._from.row = cell.row  # type: ignore[union-attr]
    anchor.to.col = (  # type: ignore[union-attr]
        _REPORT_CHART_WIDTH + cell.column
    )
    anchor.to.row = (  # type: ignore[union-attr]
        _REPORT_CHART_HEIGHT + cell.row - 1
    )
    chart.anchor = anchor  # type: ignore[assignment]
    image = ws._images[_REPORT_FOOTER_INDEX]  # type: ignore[attr-defined]
    cell = ws[_REPORT_FOOTER_ANCHOR].offset(nrow - 1)
    image.anchor = cell.coordinate


def _edit_chart(
    ws: Worksheet,
    min_date: date,
    max_date: date,
    p_init: float,
    p_bubble: float,
) -> None:
    chart = ws._charts[_REPORT_CHART_INDEX]  # type: ignore[attr-defined]
    chart.x_axis.scaling.min = to_excel(min_date.replace(day=1))
    chart.x_axis.scaling.max = to_excel(
        max_date.replace(day=1) + relativedelta(months=1)
    )
    for series in chart.series:
        if series.title.value == "Pнач":
            series.yVal.numLit.pt[0].v = p_init
            series.yVal.numLit.pt[1].v = p_init
        elif series.title.value == "Pнас":
            series.yVal.numLit.pt[0].v = p_bubble
            series.yVal.numLit.pt[1].v = p_bubble
        else:
            for ref in (series.xVal.numRef, series.yVal.numRef):
                if ref is not None:
                    ref.f = ref.f.replace(
                        _REPORT_SHEET_NAME, quote_sheetname(ws.title)
                    )


def _process_drawings(
    ws: Worksheet,
    tests: pd.DataFrame,
    pvt: pd.DataFrame,
    isobars: Image | None,
) -> None:
    _edit_chart(
        ws,
        tests["end_date"].min(),
        tests["end_date"].max(),
        pvt["p_init"].iat[0],
        pvt["p_bubble"].iat[0],
    )
    _shift_drawings(ws, tests.shape[0])
    if isobars is not None:
        resized_isobars = _resize_isobars(isobars)
        cell = ws[_REPORT_ISOBARS_ANCHOR].offset(tests.shape[0] - 1)
        ws.add_image(resized_isobars, cell.coordinate)


def _fill_report_sheet(
    wb: openpyxl.Workbook,
    tests: pd.DataFrame,
    pvt: pd.DataFrame,
    isobars: Image | None,
    purpose: str,
) -> None:
    grouped_tests = tests.groupby("reservoir")
    reservoirs = list(map(str, grouped_tests.groups.keys()))
    sheets = _copy_sheets(wb, reservoirs)
    for ws, (_, test_group), (_, pvt_group) in zip(
        sheets, grouped_tests, pvt.groupby("reservoir")
    ):
        current_test = test_group.iloc[-1].to_dict()
        test_date = current_test["end_date"].strftime("%d.%m.%Y")
        ws[_REPORT_CELL_TITLE].value = (
            f"Результаты"
            f" {current_test['well_test']}"
            f" {current_test['well']}"
            f" {current_test['field']}"
            f"\n{test_date}"
        )
        ws[_REPORT_CELL_DATE].value = test_date
        ws[_REPORT_CELL_RESERVOIR].value = current_test["reservoir"]
        ws[_REPORT_CELL_PURPOSE].value = purpose
        _fill_test_history(ws, test_group)
        _process_drawings(ws, test_group, pvt_group, isobars)


def _process_data(
    results: list[WellTestResult],
    gtms: pd.DataFrame,
    tests: pd.DataFrame,
    neighbs: pd.DataFrame,
    neighb_tests: pd.DataFrame,
    pvt: pd.DataFrame,
    path: Path,
    template: Path,
) -> None:
    result = path / template.name
    tests = _concat_tests(tests, results)
    neighb_tests = _add_distance(neighb_tests, neighbs)
    try:
        wb = openpyxl.load_workbook(template)
        _fill_data_sheet(wb, gtms, tests, neighb_tests)
        _fill_report_sheet(
            wb, tests, pvt, results[0]["isobars"], results[0]["purpose"]
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
    pvt = await dao.get_pvt(
        results[0]["field"], results[0]["well"], reservoirs
    )
    await pool.run(
        _process_data,
        results,
        gtms,
        tests,
        neighbs,
        neighb_tests,
        pvt,
        path,
        template,
    )
    make_archive(str(path), "zip", root_dir=path)
