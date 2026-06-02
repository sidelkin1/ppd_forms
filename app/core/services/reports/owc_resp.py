from pathlib import Path
from shutil import make_archive

import openpyxl
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.writer.excel import save_workbook

from app.core.models.dto.db.field_list import UneftFieldDB
from app.core.models.dto.db.reservoir_list import UneftReservoirDB
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.dao.sql.reporters import OwcRespReporter

_CELL_FIELD_NAME = "B1"
_CELL_RESERVOIT_NAME = "B2"
_CELL_WELL_NAME = "B3"
_CELL_WELL_MODE = "B4"
_CELL_ELEVATION = "B5"
_CELL_OWC_ABS_DEPTH = "B6"
_CELL_TOP_PERF_DEPTH = "B7"
_CELL_MEASURED_PRESSURE = "B8"
_CELL_MEASURED_DEPTH = "B9"
_CELL_OIL_DENSITY = "B12"
_CELL_WATER_DENSITY = "B13"
_CELL_WATERCUT = "B14"


def _fill_properties(
    ws: Worksheet,
    props: pd.DataFrame,
    pressure: float,
    depth: float,
) -> None:
    ws[_CELL_FIELD_NAME].value = props["field"].item()
    ws[_CELL_RESERVOIT_NAME].value = props["reservoir"].item()
    ws[_CELL_WELL_NAME].value = props["well"].item()
    ws[_CELL_WELL_MODE].value = props["well_mode"].item()
    ws[_CELL_ELEVATION].value = props["elevation"].item()
    ws[_CELL_OWC_ABS_DEPTH].value = props["abs_depth_owc"].item()
    ws[_CELL_TOP_PERF_DEPTH].value = props["top_perf"].item()
    ws[_CELL_MEASURED_PRESSURE].value = pressure
    ws[_CELL_MEASURED_DEPTH].value = depth
    ws[_CELL_OIL_DENSITY].value = props["layer_oil_density"].item()
    ws[_CELL_WATER_DENSITY].value = props["water_density"].item()
    ws[_CELL_WATERCUT].value = props["watercut"].item()


def _fill_depth(ws: Worksheet, depths: pd.DataFrame) -> None:
    for row in dataframe_to_rows(depths, index=False, header=False):
        ws.append(row)


def _process_data(
    dfs: dict[str, pd.DataFrame],
    pressure: float,
    depth: float,
    path: Path,
    template: Path,
):
    result = path / template.name
    try:
        wb = openpyxl.load_workbook(template)
        _fill_properties(wb["Пересчет"], dfs["props"], pressure, depth)
        _fill_depth(wb["Глубины"], dfs["depths"])
        save_workbook(wb, result)
    finally:
        wb.close()


async def owc_resp_report(
    path: Path,
    template: Path,
    field: UneftFieldDB,
    reservoir: UneftReservoirDB,
    well: str,
    pressure: float,
    depth: float,
    dao: OwcRespReporter,
    pool: ProcessPoolManager,
) -> None:
    dfs = await dao.read_all(
        field_id=field.id, reservoir_id=reservoir.id, well=well
    )
    await pool.run(
        _process_data,
        dfs,
        pressure,
        depth,
        path,
        template,
    )
    make_archive(str(path), "zip", root_dir=path)
