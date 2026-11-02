from pathlib import Path

import pandas as pd

from app.core.services.reports.isobar import _previous_misses, _write_misses


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

    target = tmp_path / "СВОДНЫЙ_ИЗОБАРЫ_01.10.2026.xlsm"
    name = _write_misses(missed, target)
    assert name == "СВОДНЫЙ_ИЗОБАРЫ_01.10.2026_нет_строки_в_сводной.csv"
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
