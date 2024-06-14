import pandas as pd

excel_options = {
    "converters": {
        "№ скв": str,
        "Дата ВНР": lambda x: pd.to_datetime(
            x, format=r"%d.%m.%Y", errors="coerce"
        ).date(),
        "Фактический ремонт": lambda x: pd.to_datetime(
            x, format=r"%d.%m.%Y", errors="coerce"
        ).date(),
    },
    "sheet_name": 0,
    "header": 0,
    "usecols": [
        "Мест-е",
        "№ скв",
        "ГТМ скорректированный",
        "Объект разработки до ГТМ",
        "Объект разработки после ГТМ",
        "Дата ВНР",
        "Фактический ремонт",
    ],
}

column_names = [
    "field",
    "well",
    "gtm_name",
    "reservoir_before",
    "reservoir_after",
    "vnr_date",
    "start_date",
]
