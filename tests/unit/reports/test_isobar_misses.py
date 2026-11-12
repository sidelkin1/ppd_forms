from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from app.core.services.reports.isobar.columns import (
    LOST_HEADERS,
    LOST_TESTS_HEADERS,
)
from app.core.services.reports.isobar.diagnostics import (
    _previous_misses,
    _write_lost_values,
    _write_misses,
)


def test_previous_misses(tmp_path: Path) -> None:
    stock = pd.DataFrame(
        {
            "field": ["F1", "F1", "F2", "F3"],
            "well_name": ["W1", "W2", "W3", "W4"],
            "cid": ["Тур(Руд)", "Вр", "Бш", "Двн"],
        }
    )
    previous = pd.DataFrame(
        {
            "field": ["F1", "F1", "F2"],
            "well": ["W1", "W2", "W3"],
            "reservoir": ["Тур", "Вр", "Вр+Бш"],
        }
    )
    missed = _previous_misses(stock, previous)
    # W2 нашёл пару, W4 отсутствует в сводной вовсе
    assert missed["well_name"].tolist() == ["W1", "W3"]
    assert missed["cid"].tolist() == ["Тур(Руд)", "Бш"]
    assert missed["file_reservoir"].tolist() == ["Тур", "Вр+Бш"]

    message = _write_misses(tmp_path, date(2026, 10, 1), missed)
    assert message is not None
    name = "СВОДНЫЙ_ИЗОБАРЫ_01.10.2026_нет_строки_в_сводной.csv"
    assert name in message
    assert "для 2 объектов" in message
    text = (tmp_path / name).read_text(encoding="utf-8-sig")
    assert "Месторождение;Скважина;Объект в фонде" in text
    assert "F1;W1;Тур(Руд);Тур" in text


def test_previous_misses_empty() -> None:
    stock = pd.DataFrame(columns=["field", "well_name", "cid"])
    missed = _previous_misses(stock, pd.DataFrame())
    assert missed.empty
    assert list(missed.columns) == [
        "field",
        "well_name",
        "cid",
        "file_reservoir",
    ]


def _lost_frame(**extra: object) -> pd.DataFrame:
    data: dict[str, object] = {
        "field": ["F1"],
        "well": ["W1"],
        "reservoir": ["Тур"],
        "well_test": ["КВД"],
        "resp": [150.0],
        "end_date": [date(2026, 6, 1)],
    }
    return pd.DataFrame({**data, **extra})


def test_write_lost_values_previous_headers(tmp_path: Path) -> None:
    """В файле по предыдущей сводной оценки (curator) нет."""
    message = _write_lost_values(
        tmp_path,
        date(2026, 10, 1),
        _lost_frame(),
        "нет_в_фонде_сводная",
        "предыдущей сводной",
        LOST_HEADERS,
    )
    assert message is not None
    name = "СВОДНЫЙ_ИЗОБАРЫ_01.10.2026_нет_в_фонде_сводная.csv"
    header = (tmp_path / name).read_text(encoding="utf-8-sig").splitlines()[0]
    assert header == (
        "Месторождение;Скважина;Объект;Вид исследования;Рпл;Дата"
    )


def test_write_lost_values_requires_columns(tmp_path: Path) -> None:
    """Заголовки не совпали с кадром — падение, а не обрезанный файл."""
    with pytest.raises(KeyError):
        _write_lost_values(
            tmp_path,
            date(2026, 10, 1),
            _lost_frame(),
            "нет_в_фонде_welltest",
            "текущих замеров",
            LOST_TESTS_HEADERS,
        )
