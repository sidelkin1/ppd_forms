from app.infrastructure.db.mappers import well_no_branch_mapper

excel_options = {
    "converters": {
        "Скважина №": lambda s: well_no_branch_mapper[str(s)],
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

column_names = ["field", "reservoir", "well", "neighbs"]
