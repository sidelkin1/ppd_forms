from typing import Any

excel_options: dict[str, Any] = {
    "converters": {"Месторождение": str, "скв.": str},
    "sheet_name": "фонд ППД",
    "header": 2,
    "usecols": ["Месторождение", "скв."],
}

column_names: list[str] = ["field", "well"]
