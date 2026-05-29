from pathlib import Path
from shutil import make_archive

import openpyxl
import pandas as pd
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
_CELL_MEASURED_DEPTH_OFFSET = "B10"
_CELL_TOP_PERF_DEPTH_OFFSET = "B11"
_CELL_OIL_DENSITY = "B12"
_CELL_WATER_DENSITY = "B13"
_CELL_WATERCUT = "B14"


def _process_data(
    field: UneftFieldDB,
    reservoir: UneftReservoirDB,
    well: str,
    props: pd.DataFrame,
    path: Path,
    template: Path,
):
    result = path / template.name
    try:
        wb = openpyxl.load_workbook(template)
        ws = wb["Пересчет"]
        ws[_CELL_FIELD_NAME] = field.name
        ws[_CELL_RESERVOIT_NAME] = reservoir.name
        ws[_CELL_WELL_NAME] = well
        ws[_CELL_WELL_MODE] = props["well_mode"].item()
        ws[_CELL_ELEVATION] = props["elevation"].item()
        ws[_CELL_OWC_ABS_DEPTH] = props["abs_depth_owc"].item()
        ws[_CELL_TOP_PERF_DEPTH] = props["top_perf"].item()
        # ws[_CELL_MEASURED_PRESSURE] = props["measured_pressure"].item()
        # ws[_CELL_MEASURED_DEPTH] = props["measured_depth"].item()
        # ws[_CELL_MEASURED_DEPTH_OFFSET] = props["measured_depth_offset"].item()
        # ws[_CELL_TOP_PERF_DEPTH_OFFSET] = props["top_perf_depth_offset"].item()
        ws[_CELL_OIL_DENSITY] = props["layer_oil_density"].item()
        ws[_CELL_WATER_DENSITY] = props["water_density"].item()
        ws[_CELL_WATERCUT] = props["watercut"].item()
        save_workbook(wb, result)
    finally:
        wb.close()


async def owc_resp_report(
    path: Path,
    template: Path,
    field: UneftFieldDB,
    reservoir: UneftReservoirDB,
    well: str,
    dao: OwcRespReporter,
    pool: ProcessPoolManager,
) -> None:
    props = await dao.read_one(
        field_id=field.id, reservoir_id=reservoir.id, well=well
    )
    await pool.run(
        _process_data, field, reservoir, well, props, path, template
    )
    make_archive(str(path), "zip", root_dir=path)
