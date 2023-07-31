from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.utils import run_in_process
from app.crud.queryset.local.profile_report import select_profile_report
from app.services.save_dataframe import save_to_csv


def group_diff_absorb(df: pd.DataFrame) -> pd.DataFrame:
    columns = df.columns.difference(('diff_absorp', 'remarks'), sort=False)
    df['diff_absorp'] /= df.groupby(level=0)['diff_absorp'].transform(len)
    return df.groupby(columns.to_list(), as_index=False).agg({
        'diff_absorp': sum,
        'remarks': (lambda s: (
            s[s.str.contains(r'\w+', na=False)]
            .drop_duplicates()
            .str.cat(sep=',')
        )),
    })


def calc_layer_rate(df: pd.DataFrame, rate: str) -> pd.DataFrame:
    df = df.eval(f'{rate}_layer={rate}_all*diff_absorp/100')
    df[f'{rate}_layer'].fillna(df[rate], inplace=True)
    df[rate] = df[rate].mul(df['1/num_layer'], fill_value=1)
    return df


def calc_layer_rates(df: pd.DataFrame) -> pd.DataFrame:
    columns = ['field', 'well_name', 'cid', 'rec_date']
    df['1/num_layer'] = 1 / df.groupby(columns)['layer'].transform(len)
    df = calc_layer_rate(df, 'liq_rate')
    df = calc_layer_rate(df, 'inj_rate')
    return df


def process_data(data: list[Row]) -> pd.DataFrame:
    df = pd.DataFrame(data)
    df['layer'] = df['layer'].str.split(settings.delimiter)
    df = df.explode('layer')
    df['layer'].fillna('', inplace=True)
    df = group_diff_absorb(df)
    df = calc_layer_rates(df)
    return df


async def create_report(
    path: Path,
    date_from: date,
    date_to: date,
    session: AsyncSession,
    pool: ProcessPoolExecutor,
) -> None:
    result = await session.execute(
        select_profile_report(date_from, date_to)
    )
    df = await run_in_process(pool, process_data, result.all())
    await save_to_csv(df, path)
