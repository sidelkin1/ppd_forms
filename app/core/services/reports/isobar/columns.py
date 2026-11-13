"""Колонки, форматы и заголовки сводной «Изобары»."""

from app.core.models.enums import IsobarStatus

SHEET = "текущие отборы"
FIRST_ROW = 2
LAST_COLUMN = 54  # BB

COL_FIELD = 3  # C
COL_RESERVOIR = 4  # D
COL_WELL = 5  # E
COL_TYPE = 6  # F
COL_STATUS = 7  # G
COL_PRESSURE_GDI = 8  # H (формула)
COL_BHP = 9  # I
COL_PREV_RESP = 10  # J
COL_PREV_DATE = 11  # K
COL_PREV_TEST = 12  # L
COL_PREV_TYPE = 13  # M
COL_PREV_STATUS = 14  # N
COL_RESP = 15  # O
COL_DATE = 16  # P
COL_WELL_TEST = 17  # Q
COL_FAILED_RESP = 29  # AC
COL_FAILED_DATE = 30  # AD
COL_FAILED_TEST = 31  # AE
COL_BUBBLE = 34  # AH

DATE_COLUMNS = (COL_PREV_DATE, COL_DATE, COL_FAILED_DATE)
DATE_FORMAT = "DD.MM.YYYY"
OUTPUT_PREFIX = "СВОДНЫЙ_ИЗОБАРЫ"

MISS_HEADERS = {
    "field": "Месторождение",
    "well_name": "Скважина",
    "cid": "Объект в фонде",
    "file_reservoir": "Объекты в предыдущей сводной",
}
STATE_HEADERS = {
    "field": "Месторождение",
    "well": "Скважина",
    "end_date": "Дата замера",
    "reservoir": "Объект",
    "well_test": "Вид исследования",
    "resp": "Рпл",
}
LOST_HEADERS = {
    "field": "Месторождение",
    "well": "Скважина",
    "reservoir": "Объект",
    "well_test": "Вид исследования",
    "resp": "Рпл",
    "end_date": "Дата",
}
# у замеров welltest есть оценка (curator), у строк предыдущей сводной — нет
LOST_TESTS_HEADERS = {**LOST_HEADERS, "curator": "Оценка"}

VALUE_COLUMNS = {
    COL_FIELD: "field",
    COL_RESERVOIR: "reservoir",
    COL_WELL: "well_name",
    COL_TYPE: "type_",
    COL_STATUS: "status",
    COL_BHP: "p_bhp",
    COL_PREV_RESP: "prev_resp",
    COL_PREV_DATE: "prev_date",
    COL_PREV_TEST: "prev_well_test",
    COL_PREV_TYPE: "state_type",
    COL_PREV_STATUS: "state_status",
    COL_RESP: "current_resp",
    COL_DATE: "current_date",
    COL_WELL_TEST: "current_well_test",
    COL_FAILED_RESP: "failed_resp_owc",
    COL_FAILED_DATE: "failed_end_date",
    COL_FAILED_TEST: "failed_well_test",
    COL_BUBBLE: "p_bubble",
}
SKIP_FORMULA_COLUMNS = (COL_BHP, COL_BUBBLE)
REQUIRED_FORMULA_COLUMNS = (1, 2, COL_PRESSURE_GDI)  # A, B, H

LOST_COLUMNS = (
    "field",
    "well",
    "reservoir",
    "well_test",
    "resp",
    "end_date",
)

# Состояния, которых нет в справочнике: чтобы их было видно на фоне
# остальных, пишем в скобках, курсивом и своим цветом.
SYNTHETIC_STATUS_COLORS = {
    IsobarStatus.old_wellbore.value: "FF808080",  # серый
    IsobarStatus.open_perf.value: "FF2E75B6",  # синий
}
