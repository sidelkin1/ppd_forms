from datetime import date

import pytest

from app.core.models.schemas.isobar_params import (
    IsobarParams,
    parse_previous_date,
)

FILE = "СВОДНЫЙ_ИЗОБАРЫ_01.07.2026.xlsm"


def test_parse_previous_date():
    assert parse_previous_date(FILE) == date(2026, 7, 1)


def test_params_derives_dates():
    params = IsobarParams(file=FILE)
    assert params.previous_date == date(2026, 7, 1)
    assert params.on_date == date(2026, 10, 1)
    assert params.stock_date == date(2026, 9, 1)


@pytest.mark.parametrize(
    "filename",
    [
        "СВОДНЫЙ_ИЗОБАРЫ_01.07.2026.xlsx",
        "СВОДНЫЙ_ИЗОБАРЫ.xlsm",
        "СВОДНЫЙ_ИЗОБАРЫ_31.02.2026.xlsm",
        "СВОДНЫЙ_ИЗОБАРЫ_15.07.2026.xlsm",
        "../СВОДНЫЙ_ИЗОБАРЫ_01.07.2026.xlsm",
        "../../other/СВОДНЫЙ_ИЗОБАРЫ_01.07.2026.xlsm",
        "/tmp/СВОДНЫЙ_ИЗОБАРЫ_01.07.2026.xlsm",
    ],
)
def test_parse_previous_date_errors(filename):
    with pytest.raises(ValueError):
        parse_previous_date(filename)


@pytest.mark.parametrize(
    ("file", "on_date", "stock_date"),
    [
        (FILE, date(2026, 10, 1), date(2026, 9, 1)),
        # переход через границу года
        (
            "СВОДНЫЙ_ИЗОБАРЫ_01.11.2026.xlsm",
            date(2027, 2, 1),
            date(2027, 1, 1),
        ),
    ],
)
def test_params_derives_dates_across_year(file, on_date, stock_date):
    params = IsobarParams(file=file)
    assert params.on_date == on_date
    assert params.stock_date == stock_date


def test_params_rejects_bad_file():
    with pytest.raises(ValueError):
        IsobarParams(file="СВОДНЫЙ_ИЗОБАРЫ.xlsm")


def test_params_forbids_extra_fields():
    with pytest.raises(ValueError):
        IsobarParams(file=FILE, on_date="2026-10-01")
