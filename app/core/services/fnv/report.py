import asyncio
from datetime import date
from pathlib import Path
from shutil import make_archive

import aiofiles
import numpy as np
import pandas as pd
from structlog.stdlib import BoundLogger

from app.core.models.dto import UneftFieldDB
from app.core.services.fnv.context import LogContext
from app.infrastructure.db.dao.sql.reporters import FnvReporter

"""
Немного переработанная версия пакета
https://github.com/TsepelevVP/PyOraFNV

"""


class FnvException(Exception):
    pass


def _prepare_profile(poro: pd.DataFrame) -> pd.DataFrame:
    hmin = poro["ktop"].min()
    hmax = poro["kbot"].max()
    profile = pd.DataFrame(
        columns=[
            "MD",
            "layer_name",
            "cid",
            "xcoord",
            "ycoord",
            "poro",
            "h_eff",
        ]
    )
    # не нужен self.max+1, т.к. интервал определеяется минимальной глубиной
    profile["MD"] = range(hmin, hmax)
    profile["h_eff"] = 0.0
    profile["layer_name"] = ""
    return profile


def _fill_properties(
    profile: pd.DataFrame, poro: pd.DataFrame
) -> pd.DataFrame:
    for _, row in poro.iterrows():
        # закрывающее < , т.к. интервал определяется минимальной глубиной
        flt = (profile["MD"] >= row["ktop"]) & (profile["MD"] < row["kbot"])
        profile.loc[flt, "layer_name"] = row["layer_name"]
        profile.loc[flt, "cid"] = row["cid"]
        profile.loc[flt, "xcoord"] = row["xcoord"]
        profile.loc[flt, "ycoord"] = row["ycoord"]
        profile.loc[flt, "poro"] = row["poro"]
        profile.loc[flt, "h_eff"] = row["h"]
    return profile


async def _fill_events(
    profile: pd.DataFrame, events: pd.DataFrame, logger: BoundLogger
) -> pd.DataFrame:
    profile["last_perf"] = 0.0
    profile["1900-01-01"] = 0.0
    for _, row in events.iterrows():
        # в ГДИ часто негерметы обозначают интервалом
        # с одинаковымы глубинами :(
        # ? возможно лучше вместо +0.1 делать base = self.hmax
        if row["top"] == row["base"]:
            row["base"] = row["base"] + 0.1
            # row['base'] = self.hmax
        flt = (profile["MD"] >= row["top"]) & (profile["MD"] < row["base"])
        # данные об одном событии приходят в нескольких строках events
        # если нет еще столбца с такой датой -
        # значит событие пришло в первый раз
        if row["date_op"] not in profile.columns:
            if row["type_action"] == "GDI":
                # если GDI - обнуляем
                profile[row["date_op"]] = 0.0
            else:
                # если перфорация или заливка -
                # берем последний актуальный профиль по перфорациям
                profile[row["date_op"]] = profile["last_perf"]
        # разбираем события
        if row["type_action"] == "GDI":
            # ГДИ - добавляем долю притока из ГДИ
            # делим на количество единичных интервалов,
            # т.к. профиль по ГДИ дается на весь интервал притока целиком
            # можно для надежности взять
            # self.profile.loc[flt, row['date_op']].count(),
            # но вычисление по глубинам должно быть быстрее
            profile.loc[flt, row["date_op"]] = row["prof"] / (
                row["base"] - row["top"]
            )
        elif row["type_action"] == "PERFORATION":
            # перфорация - добавляем вскрытую мощность
            profile.loc[flt, row["date_op"]] = 1.0
            # заменяем последнее состояние перфораций
            profile["last_perf"] = profile[row["date_op"]]
        else:
            # заливка - обнуляем приток
            profile.loc[flt, row["date_op"]] = 0.0
            # заменяем последнее состояние перфораций
            profile["last_perf"] = profile[row["date_op"]]
        # выводим данные по получившемуся профилю в лог
        log_df = profile.loc[flt, "layer_name"].unique()
        await logger.ainfo(
            "Событие: %s (%s - %s): %s %s %s",
            row["date_op"],
            row["top"],
            row["base"],
            row["type_action"],
            "" if not row["prof"] else int(row["prof"] * 100),
            log_df,
        )
    # добавить в профиль последний столбец с текущей датой -
    # нужно будет при расчете закачки поинтервально
    # обнуляем последний столбец
    profile[date.today().strftime("%Y-%m-%d")] = 0.0
    return profile


def _normalize_profile(profile: pd.DataFrame) -> pd.DataFrame:
    i_col_start = profile.columns.get_loc("h_eff")
    for name, values in profile.iloc[:, i_col_start + 1 :].items():
        total = np.sum(values)
        if total == 0:
            profile[name] = 0.0
        else:
            profile[name] = profile[name] / total
    return profile


async def _get_profile(
    poro: pd.DataFrame, events: pd.DataFrame, logger: BoundLogger
) -> pd.DataFrame:
    poro["ktop"] = poro["ktop"].mul(100).fillna(0).astype("int")
    poro["kbot"] = poro["kbot"].mul(100).fillna(0).astype("int")
    events["top"] = events["top"].mul(100).fillna(0).astype("int")
    events["base"] = events["base"].mul(100).fillna(0).astype("int")
    events["date_op"] = events["date_op"].dt.strftime("%Y-%m-%d")
    events["prof"] = events["prof"] * 0.01
    profile = _prepare_profile(poro)
    profile = _fill_properties(profile, poro)
    profile = await _fill_events(profile, events, logger)
    profile = _normalize_profile(profile)
    return profile


async def _calc_injection(
    uwi: str,
    profile: pd.DataFrame,
    dao: FnvReporter,
    logger: BoundLogger,
) -> pd.DataFrame:
    await logger.ainfo("-" * 160)
    await logger.ainfo(
        "Создан профиль долей закачки: %s (%s - %s)",
        uwi,
        profile["MD"].min() / 100,
        profile["MD"].max() / 100,
    )
    await logger.ainfo("-" * 160)
    i_start_col = profile.columns.get_loc("last_perf") + 1
    # получаем профиль закачки - проходим все столбцы
    # с датами (начинаются с i_start_col)
    for index in range(i_start_col, len(profile.columns) - 1):
        # этот столбец будет содержать профиль
        # закачки по минимальным интервалам
        # раньше было index+1 - это неверно!
        # т.к. перфорации актуальны на начало интервала, а не на конец
        # чтобы не добавлять после цикла вручную интервал до текущей даты,
        # она была добавлена в WellProfile.init() последним столбцом
        current = profile.columns[index]
        # закачка за период между событиями
        totwat = await dao.totwat(
            uwi, profile.columns[index], profile.columns[index + 1]
        )
        # профиль притока по интервалу = доля закачки * на закачку
        profile[current] = profile[current] * totwat
        # сделать список названий пластов с непустым притоком в log_df
        log_df = profile[profile[current] != 0]["layer_name"].unique()
        await logger.ainfo(
            "%s Закачка (%s - %s) : %.0f, по профилю : %.0f %s",
            uwi,
            profile.columns[index],
            profile.columns[index + 1],
            totwat,
            profile[current].sum(),
            log_df,
        )
    # суммируем столбцы, начиная с 5-го
    profile["total"] = profile.iloc[:, i_start_col:].sum(axis=1)
    # вывести строки с непустым названием пласта и непустым последним столбцом
    await logger.ainfo("-" * 160)
    await logger.ainfo(
        "%s Всего закачка по профилям: %s", uwi, profile["total"].sum()
    )
    await logger.adebug(
        "Ненулевые профили закачки:\n%s",
        profile[(profile["layer_name"] != "") & (profile.iloc[:, -1] > 0)],
    )
    return profile


async def _calc_radius(
    uwi: str, profile: pd.DataFrame, logger: BoundLogger
) -> pd.DataFrame:
    layers_radius = profile.groupby(["layer_name"]).agg(
        {
            "cid": "first",
            "xcoord": "first",
            "ycoord": "first",
            "total": "sum",
            "poro": "mean",
            "h_eff": "mean",
        }
    )
    layers_radius["radius"] = np.sqrt(
        layers_radius["total"].astype("float64")
        / (
            np.pi
            * layers_radius["poro"].astype("float64")
            * layers_radius["h_eff"].astype("float64")
        )
    )
    # заменяем не-числа на 0
    layers_radius = layers_radius.infer_objects().fillna(0)
    await logger.ainfo("-" * 160)
    await logger.ainfo("%s Радиусы ФНВ по пластам:", uwi)
    await logger.ainfo("\n%s", layers_radius)
    return layers_radius


async def _calc_contours(
    uwi: str,
    layers_radius: pd.DataFrame,
    min_radius: float,
    logger: BoundLogger,
) -> pd.DataFrame:
    result = pd.DataFrame(columns=["contour"], index=layers_radius.index)
    await logger.ainfo("-" * 160)
    # по всем строкам layers_radius
    for index, row in layers_radius.iterrows():
        r = row["radius"]
        x = row["xcoord"]
        y = row["ycoord"]
        contour = list()
        if r > min_radius:
            contour = [
                [
                    r * np.cos(phi * 2 * np.pi / 50) + x,
                    r * np.sin(phi * 2 * np.pi / 50) + y,
                ]
                for phi in range(51)
            ]
            await logger.ainfo(
                "%s Круг для %s : (%s - %s) R = %s", uwi, index, x, y, r
            )
        result.loc[index, "contour"] = contour  # type:ignore
    result.columns = [uwi]  # type:ignore
    return result


async def _calc_profile(
    uwi: str,
    poro: pd.DataFrame,
    events: pd.DataFrame,
    min_radius: float,
    dao: FnvReporter,
    logger: BoundLogger,
) -> pd.DataFrame:
    profile = await _get_profile(poro, events, logger)
    profile = await _calc_injection(uwi, profile, dao, logger)
    layers_radius = await _calc_radius(uwi, profile, logger)
    contours = await _calc_contours(uwi, layers_radius, min_radius, logger)
    return contours


async def _process_well(
    uwi: str,
    min_radius: float,
    alternative: bool,
    dao: FnvReporter,
    logger: BoundLogger,
) -> pd.DataFrame:
    await logger.ainfo("-" * 160)
    await logger.ainfo(">>> Скважина: %s", uwi)
    poro = await dao.poro(uwi)
    await logger.ainfo("Пористость: %s", uwi)
    if not poro.size:
        raise FnvException("нет пористости")
    await logger.ainfo("\n%s", poro)
    events = await dao.events(alternative, uwi)
    await logger.ainfo("События: %s", uwi)
    contours = await _calc_profile(uwi, poro, events, min_radius, dao, logger)
    await logger.ainfo("%s Созданы контуры ФНВ", uwi)
    await logger.adebug("%s", contours)
    return contours


async def _make_contours(
    field: UneftFieldDB,
    min_radius: float,
    alternative: bool,
    dao: FnvReporter,
    logger: BoundLogger,
) -> pd.DataFrame:
    well_names = await dao.cumwat(field.id)
    await logger.ainfo(
        "Скважин в ППД: %s Накопленная закачка: от %s м3 до %s м3",
        well_names["uwi"].count(),
        well_names["cumwat"].min(),
        well_names["cumwat"].max(),
    )
    final_contours = await dao.layers(field.id)
    final_contours = final_contours.groupby(["cid", "layer_name"]).agg("first")
    for _, row in well_names.iterrows():
        uwi = row["uwi"]
        try:
            contours = await _process_well(
                uwi, min_radius, alternative, dao, logger
            )
            final_contours = pd.merge(
                final_contours,
                contours,
                how="left",
                left_index=True,
                right_index=True,
            )
        except FnvException as error:
            await logger.aexception(
                "Не обработана скважина: %s : %s", uwi, error
            )
    final_contours.fillna(0, inplace=True)
    await logger.ainfo("-" * 160)
    await logger.ainfo(
        "%s: cкважин с профилями: %s",
        field.name,
        final_contours.columns.size,
    )
    await logger.adebug("%s", final_contours)
    return final_contours


async def _save_countours(
    path: Path, contours: pd.DataFrame, logger: BoundLogger
) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for layer_index, *layer_row in contours.itertuples():
        if any(layer_row):
            fname = (path / "_".join(layer_index)).with_suffix(".txt")
            async with aiofiles.open(fname, "w") as file:
                await file.write("/\n")  # цикл по контурам
                for contour in filter(None, layer_row):  # type: ignore
                    # цикл по точкам внутри контура
                    await file.writelines(
                        f"{pointx:.3f} {pointy:.3f}\n"
                        for pointx, pointy in contour
                    )
                    await file.write("/\n")
    await logger.ainfo("-" * 160)
    await logger.awarning("Сохранено в %s", path)


async def _process_field(
    path: Path,
    field: UneftFieldDB,
    min_radius: float,
    alternative: bool,
    fnv: FnvReporter,
    sem: asyncio.Semaphore,
    failures: asyncio.Queue[UneftFieldDB],
) -> None:
    async with sem:
        result_path = path / field.name
        result_path.mkdir(parents=True, exist_ok=True)
        with LogContext(str(result_path), result_path) as logger:
            try:
                await logger.awarning("Start")
                await logger.awarning("Field = %s", field.name)
                await logger.awarning("Min radius = %s", min_radius)
                await logger.awarning("Alternative = %s", alternative)
                contours = await _make_contours(
                    field, min_radius, alternative, fnv, logger
                )
                await _save_countours(result_path, contours, logger)
                await logger.awarning("Finish")
            except Exception:
                await logger.aexception("Ошибка во время обработки")
                await failures.put(field)


async def _handle_failures(
    path: Path,
    failures: asyncio.Queue[UneftFieldDB],
    tasks: list[asyncio.Task],
) -> None:
    with LogContext(str(path), path) as logger:
        while not (all(task.done() for task in tasks) and failures.empty()):
            if failures.empty():
                await asyncio.sleep(0)
                continue
            field = await failures.get()
            await logger.aerror(
                "Не удалось обработать месторождение: %s", field.name
            )


async def fnv_report(
    path: Path,
    fields: list[UneftFieldDB],
    min_radius: float,
    alternative: bool,
    max_fields: int,
    fnv: FnvReporter,
) -> None:
    sem = asyncio.Semaphore(max_fields)
    failures: asyncio.Queue[UneftFieldDB] = asyncio.Queue(maxsize=100)
    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(
                _process_field(
                    path, field, min_radius, alternative, fnv, sem, failures
                )
            )
            for field in fields
        ]
        tg.create_task(_handle_failures(path, failures, tasks))
    make_archive(str(path), "zip", root_dir=path)
