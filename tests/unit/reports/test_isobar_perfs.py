from datetime import date

import pandas as pd
import pytest

from app.core.services.reports.isobar.diagnostics import _unmatched_tests
from app.core.services.reports.isobar.preparation import _resolve_branches


def _tests(
    well: str = "303", end_date: date = date(2026, 8, 1)
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "field": ["Котовское"],
            "well": [well],
            "reservoir": ["Вз"],
            "well_test": ["КВД"],
            "end_date": [end_date],
            "resp_owc": [100.0],
        }
    )


def _perfs(*intervals: tuple[str, date, date | None]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "field": ["Котовское"] * len(intervals),
            "well": ["303"] * len(intervals),
            "reservoir": ["Вз"] * len(intervals),
            "branch": [item[0] for item in intervals],
            "comp_date": [item[1] for item in intervals],
            "close_date": [item[2] for item in intervals],
        }
    )


def test_branch_from_open_perforation() -> None:
    """Ствол берётся по интервалу, открытому на дату замера."""
    perfs = _perfs(
        ("303", date(2014, 6, 10), date(2026, 5, 21)),
        ("303B2", date(2026, 5, 24), None),
    )

    resolved, fallback = _resolve_branches(
        _tests(end_date=date(2026, 8, 1)), perfs
    )

    assert resolved["branch"].tolist() == ["303B2"]
    assert fallback.empty


def test_goes_to_every_open_branch() -> None:
    """Замер привязывается ко всем стволам, открытым на его дату."""
    perfs = _perfs(
        ("303", date(2026, 1, 1), None),
        ("303B1", date(2026, 1, 1), None),
        ("303B2", date(2026, 1, 1), date(2026, 6, 1)),
    )

    resolved, fallback = _resolve_branches(_tests(), perfs)

    assert resolved["branch"].tolist() == ["303", "303B1"]
    assert len(resolved) == 2
    assert fallback.empty


def test_closed_perforations_fall_back_to_well() -> None:
    """Все интервалы закрыты на дату — ствол остаётся за скважиной."""
    perfs = _perfs(("303B2", date(2020, 5, 24), date(2021, 1, 1)))

    resolved, fallback = _resolve_branches(_tests(), perfs)

    assert resolved["branch"].tolist() == ["303"]
    assert fallback["well"].tolist() == ["303"]


def test_branch_without_perfs() -> None:
    """Пустая таблица перфораций — все замеры остаются за скважиной."""
    resolved, fallback = _resolve_branches(
        _tests(), pd.DataFrame(columns=["field", "well", "reservoir"])
    )

    assert resolved["branch"].tolist() == ["303"]
    assert fallback["well"].tolist() == ["303"]


def test_unmatched_tests_use_branch() -> None:
    """Диагностика сверяет ствол с фондом, а не скважину без ствола."""
    tests = _tests()
    tests["branch"] = ["303B2"]
    tests["curator"] = ["Хорошая"]
    stock = pd.DataFrame(
        {
            "field": ["Котовское"],
            "well_name": ["303B1"],
            "cid": ["Вз"],
        }
    )

    unmatched = _unmatched_tests(tests, stock)

    assert unmatched["well"].tolist() == ["303B2"]
    assert unmatched["resp"].tolist() == pytest.approx([100.0])
