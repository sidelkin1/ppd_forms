import pandas as pd

excel_options = {
    "header": 0,
    "converters": {
        "Скв.": str,
        "Дата ГТМ": lambda x: pd.to_datetime(
            x, format=r"%d.%m.%Y", errors="coerce"
        ).date(),
    },
    "usecols": [
        "Месторождение",
        "Скв.",
        "Дата ГТМ",
        "Нефть (1 год)",
        "Нефть (5 лет)",
        "Жидкость (1 год)",
        "Жидкость (5 лет)",
        "Отчет",
    ],
}

column_names = [
    "field",
    "well",
    "date",
    "oil_total_1",
    "oil_total_5",
    "liq_total_1",
    "liq_total_5",
    "report",
]
