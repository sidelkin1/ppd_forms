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
    ],
)
def test_parse_previous_date_errors(filename):
    with pytest.raises(ValueError):
        parse_previous_date(filename)


def test_params_rejects_bad_file():
    with pytest.raises(ValueError):
        IsobarParams(file="СВОДНЫЙ_ИЗОБАРЫ.xlsm")


def test_params_forbids_extra_fields():
    with pytest.raises(ValueError):
        IsobarParams(file=FILE, on_date="2026-10-01")
