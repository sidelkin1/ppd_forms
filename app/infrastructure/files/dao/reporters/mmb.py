from pathlib import Path

import pandas as pd
from fastapi.concurrency import run_in_threadpool


class MmbReporter:
    converters = {
        "Блок": str,
        "№ скв.": str,
        "Соединения": str,
        "Начальный поровый объем, тыс.м3": lambda x: x * 1000,
    }
    usecols = [
        "М-е",
        "№ скв.",
        "Объект",
        "Блок",
        "Начальное Pпл, атм",
        "Нач. об. коэфф. воды, м3/м3",
        "Нач. об. коэфф. нефти, м3/м3",
        "Сжимаемость воды, 1/атм",
        "Сжимаемость нефти, 1/атм",
        "Сжимаемость породы, 1/атм",
        "Начальная водонасыщенность, д.ед.",
        "Начальный поровый объем, тыс.м3",
        "Соединения",
        "Проводим. с границ. пост. Pпл, м3/атм",
        "Коэффициент продуктивности, м3/атм",
        "Коэффициент приемистости, м3/атм",
        "Эффективность закачки, д.ед.",
        "Проводимость, м3/атм",
        "Мин. расчетное Pпл, атм",
        "Макс. расчетное Pпл, атм",
        "Вязкость воды, сПз",
        "Вязкость нефти, сПз",
        "Макс. ОФП по воде, д.ед.",
        "Макс. ОФП по нефти д.ед.",
    ]
    columns = [
        "Field",
        "Well",
        "Reservoir",
        "Tank",
        "Pi",
        "Bwi",
        "Boi",
        "cw",
        "co",
        "cf",
        "Swi",
        "Vpi",
        "Neighb",
        "Tconst",
        "Prod_index",
        "Inj_index",
        "Frac_inj",
        "T",
        "Min_Pres",
        "Max_Pres",
        "muw",
        "muo",
        "krw_max",
        "kro_max",
    ]

    def __init__(self, path: Path) -> None:
        self.path = path

    async def get_description(self) -> pd.DataFrame:
        df: pd.DataFrame = await run_in_threadpool(
            pd.read_excel,  # type: ignore[arg-type]
            self.path,
            converters=self.converters,
            usecols=self.usecols,
        )
        df.columns = self.columns  # type: ignore[assignment]
        return df
