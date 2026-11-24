import asyncio
from datetime import date
from pathlib import Path
from shutil import make_archive

import numpy as np
import openpyxl
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.writer.excel import save_workbook

from app.core.models.dto.db.field_list import UneftFieldDB
from app.core.models.dto.db.reservoir_list import UneftReservoirDB
from app.core.models.enums import WellTest
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.dao.sql.reporters import OwcRespReporter

_CALCULATOR_FIELD = "B1"
_CALCULATOR_RESERVOIR = "B2"
_CALCULATOR_WELL_NAME = "B3"
_CALCULATOR_WELL_MODE = "B4"
_CALCULATOR_ELEVATION = "B5"
_CALCULATOR_OWC_ABS_DEPTH = "B6"
_CALCULATOR_TOP_PERF_DEPTH = "B7"
_CALCULATOR_MEASURED_PRESSURE = "B8"
_CALCULATOR_MEASURED_DEPTH = "B9"
_CALCULATOR_RESERVOIR_OIL_DENSITY = "B12"
_CALCULATOR_WATER_DENSITY = "B13"
_CALCULATOR_WATERCUT = "B14"

_ANALYTICS_REGION = "B5"
_ANALYTICS_WORKSHOP = "C5"
_ANALYTICS_FIELD = "E5"
_ANALYTICS_WELL_NAME = "F5"
_ANALYTICS_WELL_PAD = "G5"
_ANALYTICS_RESERVOIR = "I5"
_ANALYTICS_WELL_MODE = "J5"
_ANALYTICS_WELLBORE = "K5"
_ANALYTICS_WELL_LIFT = "L5"
_ANALYTICS_TOP_PERF_DEPTH = "M5"
_ANALYTICS_TOP_PERF_OFFSET = "N5"
_ANALYTICS_BHP = "R5"
_ANALYTICS_OIL_RATE = "S5"
_ANALYTICS_LIQ_RATE = "T5"
_ANALYTICS_WATERCUT = "U5"
_ANALYTICS_WELL_STATUS = "V5"
_ANALYTICS_INIT_RESP = "AE5"
_ANALYTICS_BUBBLE_RESP = "AF5"
_ANALYTICS_GAS_FACTOR = "AG5"
_ANALYTICS_OIL_VISCOSITY = "AH5"
_ANALYTICS_WATER_VISCOSITY = "AI5"
_ANALYTICS_LIQUID_VISCOSITY = "AJ5"
_ANALYTICS_OIL_FVF = "AK5"
_ANALYTICS_SURFACE_OIL_DENSITY = "AL5"
_ANALYTICS_WATER_DENSITY = "AM5"
_ANALYTICS_WELL_TEST_PLAN = "AW5"
_ANALYTICS_WELL_TEST_GOAL = "AX5"
_ANALYTICS_WELL_TEST_ACTUAL = "BD5"
_ANALYTICS_WELL_TEST_START_DATE = "BE5"
_ANALYTICS_WELL_TEST_END_DATE = "BF5"
_ANALYTICS_STATIC_LEVEL_DEPTH = "BL5"
_ANALYTICS_ANNULAR_PRESSURE = "BM5"
_ANALYTICS_MEASURED_DEPTH = "BN5"
_ANALYTICS_MEASURED_PRESSURE = "BO5"
_ANALYTICS_TOP_PERF_PRESSURE = "BY5"
_ANALYTICS_OWC_PRESSURE = "BZ5"

_RN_VEGA_INTERPRETATION = "Интерпретация"
_RN_VEGA_PRESSURE_SHEET = "Давление"
_RN_VEGA_WORKSHOP = "C6"
_RN_VEGA_FIELD_CODE = "C7"
_RN_VEGA_FIELD = "C8"
_RN_VEGA_PAD = "C9"
_RN_VEGA_RESERVOIR = "C10"
_RN_VEGA_WELL = "C11"
_RN_VEGA_WELL_MODE = "C13"
_RN_VEGA_WELLBORE = "C14"
_RN_VEGA_WELL_LIFT = "C15"
_RN_VEGA_WELL_RADIUS = "C16"
_RN_VEGA_DEPTH = "C17"
_RN_VEGA_PERF_INTERVAL = "C18"
_RN_VEGA_TOP_PERF = "C19"
_RN_VEGA_TOP_PERF_OFFSET = "C20"
_RN_VEGA_ELEVATION = "C23"
_RN_VEGA_WELL_STATUS = "C25"
_RN_VEGA_BHP = "C27"
_RN_VEGA_LIQ_RATE = "C28"
_RN_VEGA_OIL_RATE = "C29"
_RN_VEGA_WATERCUT = "C30"
_RN_VEGA_OWC_ABS_DEPTH = "C32"
_RN_VEGA_OIL_COMPRESSIBILITY = "C35"
_RN_VEGA_WATER_COMPRESSIBILITY = "C36"
_RN_VEGA_INIT_RESP = "C38"
_RN_VEGA_RESERVOIR_TEMPERATURE = "C39"
_RN_VEGA_BUBBLE_RESP = "C41"
_RN_VEGA_GAS_FACTOR = "C42"
_RN_VEGA_OIL_VISCOSITY = "C43"
_RN_VEGA_WATER_VISCOSITY = "C44"
_RN_VEGA_OIL_FVF = "C46"
_RN_VEGA_SURFACE_OIL_DENSITY = "C49"
_RN_VEGA_WATER_DENSITY = "C50"
_RN_VEGA_RESERVOIR_OIL_DENSITY = "C51"
_RN_VEGA_MEASURED_DEPTH = "C61"
_RN_VEGA_DEPTH_OFFSET = "C62"
_RN_VEGA_ON_DATE = "A2"
_RN_VEGA_PRESSURE_CELL = "B2"


def _fill_calculator(ws: Worksheet, props: pd.DataFrame) -> None:
    ws[_CALCULATOR_FIELD].value = props["field"].item()
    ws[_CALCULATOR_RESERVOIR].value = props["reservoir"].item()
    ws[_CALCULATOR_WELL_NAME].value = props["branch"].item()
    ws[_CALCULATOR_WELL_MODE].value = props["well_mode"].item()
    ws[_CALCULATOR_ELEVATION].value = props["elevation"].item()
    ws[_CALCULATOR_OWC_ABS_DEPTH].value = props["abs_depth_owc"].item()
    ws[_CALCULATOR_TOP_PERF_DEPTH].value = props["top_perf"].item()
    ws[_CALCULATOR_MEASURED_PRESSURE].value = props["pressure"].item()
    ws[_CALCULATOR_MEASURED_DEPTH].value = props["depth"].item()
    ws[_CALCULATOR_RESERVOIR_OIL_DENSITY].value = props[
        "reservoir_oil_density"
    ].item()
    ws[_CALCULATOR_WATER_DENSITY].value = props["water_density"].item()
    ws[_CALCULATOR_WATERCUT].value = props["watercut"].item()


def _fill_depth(ws: Worksheet, depths: pd.DataFrame) -> None:
    for row in dataframe_to_rows(depths, index=False, header=False):
        ws.append(row)


def _fill_analytics(
    ws: Worksheet, props: pd.DataFrame, well_test: WellTest
) -> None:
    on_date = pd.to_datetime(props["on_date"]).dt.strftime("%d.%m.%Y").item()
    ws[_ANALYTICS_REGION].value = props["region"].item()
    ws[_ANALYTICS_WORKSHOP].value = props["workshop"].item()
    ws[_ANALYTICS_FIELD].value = props["field"].item()
    ws[_ANALYTICS_WELL_NAME].value = props["well"].item()
    ws[_ANALYTICS_WELL_PAD].value = props["pad"].item()
    ws[_ANALYTICS_RESERVOIR].value = props["reservoir"].item()
    ws[_ANALYTICS_WELL_MODE].value = props["well_mode"].item()
    ws[_ANALYTICS_WELLBORE].value = props["wellbore"].item()
    ws[_ANALYTICS_WELL_LIFT].value = props["well_lift"].item()
    ws[_ANALYTICS_TOP_PERF_DEPTH].value = props["top_perf"].item()
    ws[_ANALYTICS_TOP_PERF_OFFSET].value = props["top_perf_offset"].item()
    ws[_ANALYTICS_WATERCUT].value = props["watercut"].item()
    ws[_ANALYTICS_WELL_STATUS].value = props["well_status"].item()
    ws[_ANALYTICS_SURFACE_OIL_DENSITY].value = props[
        "surface_oil_density"
    ].item()
    ws[_ANALYTICS_WATER_DENSITY].value = props["water_density"].item()
    ws[_ANALYTICS_WELL_TEST_START_DATE].value = on_date
    ws[_ANALYTICS_WELL_TEST_END_DATE].value = on_date
    ws[_ANALYTICS_TOP_PERF_PRESSURE].value = props["top_perf_pressure"].item()
    ws[_ANALYTICS_OWC_PRESSURE].value = props["owc_pressure"].item()
    if well_test is WellTest.static_level:
        ws[_ANALYTICS_WELL_TEST_GOAL].value = "Рпл"
        ws[_ANALYTICS_WELL_TEST_PLAN].value = "Pпл по Hст"
        ws[_ANALYTICS_WELL_TEST_ACTUAL].value = "Hст"
        ws[_ANALYTICS_STATIC_LEVEL_DEPTH].value = props["depth"].item()
        ws[_ANALYTICS_ANNULAR_PRESSURE].value = props["pressure"].item()
    elif well_test is WellTest.pressure:
        ws[_ANALYTICS_WELL_TEST_GOAL].value = "Рпл"
        ws[_ANALYTICS_WELL_TEST_PLAN].value = "Pпл"
        ws[_ANALYTICS_WELL_TEST_ACTUAL].value = "Pпл"
        ws[_ANALYTICS_MEASURED_DEPTH].value = props["depth"].item()
        ws[_ANALYTICS_MEASURED_PRESSURE].value = props["pressure"].item()
    elif well_test is WellTest.complex:
        ws[_ANALYTICS_WELL_TEST_GOAL].value = "Рпл + ФЕС пласта"
        ws[_ANALYTICS_BHP].value = props["tr_bhp"].item()
        ws[_ANALYTICS_OIL_RATE].value = props["oil_rate"].item()
        ws[_ANALYTICS_LIQ_RATE].value = props["liq_rate"].item()
        ws[_ANALYTICS_INIT_RESP].value = props["init_resp"].item()
        ws[_ANALYTICS_BUBBLE_RESP].value = props["bubble_resp"].item()
        ws[_ANALYTICS_GAS_FACTOR].value = props["gas_factor"].item()
        ws[_ANALYTICS_OIL_VISCOSITY].value = props["oil_viscosity"].item()
        ws[_ANALYTICS_WATER_VISCOSITY].value = props["water_viscosity"].item()
        ws[_ANALYTICS_LIQUID_VISCOSITY].value = (
            f"={_ANALYTICS_OIL_VISCOSITY}*(1-{_ANALYTICS_WATERCUT}/100)"
            f"+{_ANALYTICS_WATER_VISCOSITY}*{_ANALYTICS_WATERCUT}/100"
        )
        ws[_ANALYTICS_OIL_FVF].value = props["oil_fvf"].item()


def _fill_rn_vega(ws: Worksheet, pressure_ws: Worksheet, props: pd.DataFrame):
    top_perf = props["top_perf"].item()
    bottom_perf = props["bottom_perf"].item()
    ws[_RN_VEGA_WORKSHOP].value = props["workshop"].item()
    ws[_RN_VEGA_FIELD_CODE].value = props["field_code"].item()
    ws[_RN_VEGA_FIELD].value = props["field"].item()
    ws[_RN_VEGA_PAD].value = props["pad"].item()
    ws[_RN_VEGA_RESERVOIR].value = props["reservoir"].item()
    ws[_RN_VEGA_WELL].value = props["well"].item()
    ws[_RN_VEGA_WELL_MODE].value = props["well_mode"].item()
    ws[_RN_VEGA_WELLBORE].value = props["wellbore"].item()
    ws[_RN_VEGA_WELL_LIFT].value = props["well_lift"].item()
    ws[_RN_VEGA_WELL_RADIUS].value = props["well_radius"].item()
    ws[_RN_VEGA_DEPTH].value = props["depth"].item()
    if not pd.isna(top_perf) and not pd.isna(bottom_perf):
        ws[_RN_VEGA_PERF_INTERVAL].value = f"{top_perf}-{bottom_perf}"
    ws[_RN_VEGA_TOP_PERF].value = top_perf
    ws[_RN_VEGA_TOP_PERF_OFFSET].value = props["top_perf_offset"].item()
    ws[_RN_VEGA_ELEVATION].value = props["elevation"].item()
    ws[_RN_VEGA_WELL_STATUS].value = props["well_status"].item()
    ws[_RN_VEGA_BHP].value = props["tr_bhp"].item()
    ws[_RN_VEGA_LIQ_RATE].value = props["liq_rate"].item()
    ws[_RN_VEGA_OIL_RATE].value = props["oil_rate"].item()
    ws[_RN_VEGA_WATERCUT].value = props["watercut"].item()
    ws[_RN_VEGA_OWC_ABS_DEPTH].value = props["abs_depth_owc"].item()
    ws[_RN_VEGA_OIL_COMPRESSIBILITY].value = props[
        "oil_compressibility"
    ].item()
    ws[_RN_VEGA_WATER_COMPRESSIBILITY].value = props[
        "water_compressibility"
    ].item()
    ws[_RN_VEGA_INIT_RESP].value = props["init_resp"].item()
    ws[_RN_VEGA_RESERVOIR_TEMPERATURE].value = props[
        "reservoir_temperature"
    ].item()
    ws[_RN_VEGA_BUBBLE_RESP].value = props["bubble_resp"].item()
    ws[_RN_VEGA_GAS_FACTOR].value = props["gas_factor"].item()
    ws[_RN_VEGA_OIL_VISCOSITY].value = props["oil_viscosity"].item()
    ws[_RN_VEGA_WATER_VISCOSITY].value = props["water_viscosity"].item()
    ws[_RN_VEGA_OIL_FVF].value = props["oil_fvf"].item()
    ws[_RN_VEGA_SURFACE_OIL_DENSITY].value = props[
        "surface_oil_density"
    ].item()
    ws[_RN_VEGA_WATER_DENSITY].value = props["water_density"].item()
    ws[_RN_VEGA_RESERVOIR_OIL_DENSITY].value = props[
        "reservoir_oil_density"
    ].item()
    ws[_RN_VEGA_MEASURED_DEPTH].value = props["depth"].item()
    ws[_RN_VEGA_DEPTH_OFFSET].value = props["depth_offset"].item()
    pressure_ws[_RN_VEGA_ON_DATE].value = props["on_date"].dt.date.item()
    pressure_ws[_RN_VEGA_PRESSURE_CELL].value = props["pressure"].item()


def _process_calculator(
    dfs: dict[str, pd.DataFrame], path: Path, template: Path
):
    result = path / template.name
    wb = None
    try:
        wb = openpyxl.load_workbook(template)
        _fill_calculator(wb["Пересчет"], dfs["props"])
        _fill_depth(wb["Глубины"], dfs["depths"])
        save_workbook(wb, result)
    finally:
        if wb is not None:
            wb.close()


def _process_analytics(
    dfs: dict[str, pd.DataFrame],
    well_test: WellTest,
    path: Path,
    template: Path,
):
    result = path / template.name
    wb = None
    try:
        wb = openpyxl.load_workbook(template)
        _fill_analytics(wb["Лист1"], dfs["props"], well_test)
        save_workbook(wb, result)
    finally:
        if wb is not None:
            wb.close()


def _process_rn_vega(dfs: dict[str, pd.DataFrame], path: Path, template: Path):
    result = path / template.name
    wb = None
    try:
        wb = openpyxl.load_workbook(template)
        _fill_rn_vega(
            wb[_RN_VEGA_INTERPRETATION],
            wb[_RN_VEGA_PRESSURE_SHEET],
            dfs["props"],
        )
        save_workbook(wb, result)
    finally:
        if wb is not None:
            wb.close()


def _calc_pressures(
    props: pd.DataFrame, depths: pd.DataFrame, pressure: float, depth: float
) -> pd.DataFrame:
    props[["pressure", "depth"]] = pressure, depth
    props[["depth_offset", "top_perf_offset"]] = (
        np.interp(
            (depth, props["top_perf"].item()), depths["md"], depths["offset"]
        )
        if not depths.empty
        else (np.nan, np.nan)
    )
    props["liquid_density"] = (
        props["reservoir_oil_density"] * (1 - props["watercut"] / 100)
        + props["water_density"] * props["watercut"] / 100
    )
    props["top_perf_pressure"] = (
        props["pressure"]
        + (
            (props["top_perf"] - props["top_perf_offset"])
            - (props["depth"] - props["depth_offset"])
        )
        * props["liquid_density"]
        / 10
    )
    props["owc_pressure"] = (
        props["pressure"]
        + (
            props["abs_depth_owc"]
            - (props["depth"] - props["depth_offset"] - props["elevation"])
        )
        * props["liquid_density"]
        / 10
    )
    return props


def _check_props(
    props: pd.DataFrame,
    field: UneftFieldDB,
    reservoir: UneftReservoirDB,
    well: str,
    on_date: date,
) -> None:
    """Параметры пласта должны быть однозначны.

    Дальше ``props`` читается построчно через ``Series.item()``, поэтому
    пустая или неоднозначная выборка падает непонятной ошибкой pandas
    («can only convert an array of size 1 to a Python scalar»).
    """
    if len(props) == 1:
        return
    where = (
        f"скважине {well}, объекту «{reservoir.name}», "
        f"месторождению «{field.name}» на {on_date:%d.%m.%Y}"
    )
    if props.empty:
        raise ValueError(f"Нет данных по {where}")
    raise ValueError(
        f"Неоднозначные данные по {where}: найдено {len(props)} записей"
    )


async def owc_resp_report(
    path: Path,
    calculator_template: Path,
    analytics_template: Path,
    rn_vega_template: Path,
    field: UneftFieldDB,
    reservoir: UneftReservoirDB,
    well: str,
    pressure: float,
    depth: float,
    well_test: WellTest,
    on_date: date,
    dao: OwcRespReporter,
    pool: ProcessPoolManager,
) -> None:
    dfs = await dao.read_all(
        field_id=field.id,
        reservoir_id=reservoir.id,
        well=well,
        on_date=on_date,
    )
    _check_props(dfs["props"], field, reservoir, well, on_date)
    dfs["props"] = await pool.run(
        _calc_pressures, dfs["props"], dfs["depths"], pressure, depth
    )
    async with asyncio.TaskGroup() as tg:
        tg.create_task(
            pool.run(_process_calculator, dfs, path, calculator_template)
        )
        tg.create_task(
            pool.run(
                _process_analytics, dfs, well_test, path, analytics_template
            )
        )
        if well_test is WellTest.complex:
            tg.create_task(
                pool.run(_process_rn_vega, dfs, path, rn_vega_template)
            )
    make_archive(str(path), "zip", root_dir=path)
