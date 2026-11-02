from collections.abc import Callable

import pytest

from app.infrastructure.db.mappers import RegexMapper


@pytest.mark.parametrize(
    ("rules", "value", "expected"),
    [
        ("field", "ИМ. А.А.ЗЕЛЕНИНА", "Им. А.А. Зеленина"),
        ("field", "КАРКАШУРСКОЕ", "Каркашурское"),
        ("field", "Им. А.А. Зеленина", "Им. А.А. Зеленина"),
        ("reservoir", "Вз(02074)", "Вз(Ал)"),
        ("reservoir", "алексинский Вз(02074)", "Вз(Ал)"),
    ],
)
def test_isobar_replace_rules(
    replace_mapper: Callable[[str], RegexMapper],
    rules: str,
    value: str,
    expected: str,
) -> None:
    assert replace_mapper(rules)[value] == expected
