from typing import Any

excel_options: dict[str, Any] = {
    "converters": {
        "Скважина №": str,
        "Работающее окружение скважины (области Вороного)": str,
    },
    "sheet_name": 0,
    "usecols": [
        "Месторождение",
        "Объект",
        "Скважина №",
        "Работающее окружение скважины (области Вороного)",
    ],
}

column_names: list[str] = ["field", "reservoir", "well", "neighbs"]
