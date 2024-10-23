import pandas as pd

excel_options = {
    "converters": {
        6: str,
        57: lambda x: pd.to_datetime(
            x, format=r"%d.%m.%Y", errors="coerce"
        ).date(),
        58: lambda x: pd.to_datetime(
            x, format=r"%d.%m.%Y", errors="coerce"
        ).date(),
    },
    "sheet_name": "welltest_list",
    "header": 4,
    "usecols": [5, 7, 8, 9, 55, 56, 57, 71, 72, 73, 74, 77, 78, 80, 84],
}

column_names = [
    "well",
    "field",
    "reservoir",
    "well_type",
    "well_test",
    "start_date",
    "end_date",
    "oil_perm",
    "wat_perm",
    "liq_perm",
    "skin_factor",
    "resp_owc",
    "prod_index",
    "frac_length",
    "reliability",
]
