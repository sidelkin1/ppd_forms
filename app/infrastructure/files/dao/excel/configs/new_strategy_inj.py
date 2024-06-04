import re
from typing import Any, Callable

import pandas as pd

RESERVOIRS_WELLS_SEPARATOR = ":"

_pattern = re.compile(
    r"(?P<reservoir>[\w\-+()]*)\s*:(?P<neighbs>.*?)(?=[\w\-+()]*\s*:|$)",
    flags=re.MULTILINE,
)


def convert_neighbs_factory(delimiter: str) -> Callable[[Any], str]:
    def convert_neighbs(input_: Any) -> str:
        input_ = str(input_).replace("_x000D_", "")  # FIXME more robust way
        if groups := [m.groupdict() for m in _pattern.finditer(input_)]:
            return RESERVOIRS_WELLS_SEPARATOR.join(
                (
                    delimiter.join(group["reservoir"] for group in groups),
                    delimiter.join(group["neighbs"] for group in groups),
                )
            )
        else:
            return f"{RESERVOIRS_WELLS_SEPARATOR}{input_}"

    return convert_neighbs


def excel_options(delimiter: str) -> dict[str, Any]:
    return {
        "converters": {
            1: str,
            6: lambda x: pd.to_datetime(
                x, format=r"%d.%m.%Y", errors="coerce"
            ).date(),
            10: convert_neighbs_factory(delimiter),
        },
        "parse_dates": [4],
        "sheet_name": "Лист1",
        "header": 4,
        "usecols": [2, 4, 9, 17, 52, 72, 77, 79, 83, 84, 110],
        "na_values": "#Н/Д",
    }


column_names: list[str] = [
    "field",
    "well",
    "reservoir",
    "gtm_description",
    "gtm_date",
    "oil_recovery",
    "effect_end",
    "gtm_group",
    "oil_rate",
    "gtm_problem",
    "neighbs",
]
