import logging
from datetime import date
from pathlib import Path
from shutil import make_archive

import aiofiles
import numpy as np
import pandas as pd

from app.core.models.dto import UneftFieldDB, UneftWellDB
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.dao.sql.reporters import FnvReporter


class FnvException(Exception):
    pass


def _configure_logging(log_name: str, path: Path) -> logging.Logger:
    logger = logging.getLogger(log_name)
    format = (
        "[%(asctime)s] [%(module)s - %(funcName)s] [%(levelname)s] %(message)s"
    )
    datefmt = "%Y-%m-%d %H:%M"
    formatter = logging.Formatter(fmt=format, datefmt=datefmt)
    file_handler = logging.FileHandler(path / "fnv.log", mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger


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


def _fill_events(
    profile: pd.DataFrame, events: pd.DataFrame, logger: logging.Logger
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
        logger.info(
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


def _get_profile(
    poro: pd.DataFrame, events: pd.DataFrame, logger: logging.Logger
) -> pd.DataFrame:
    poro["ktop"] = poro["ktop"].mul(100).fillna(0).astype("int")
    poro["kbot"] = poro["kbot"].mul(100).fillna(0).astype("int")
    events["top"] = events["top"].mul(100).fillna(0).astype("int")
    events["base"] = events["base"].mul(100).fillna(0).astype("int")
    events["date_op"] = events["date_op"].dt.strftime("%Y-%m-%d")
    events["prof"] = events["prof"] * 0.01
    profile = _prepare_profile(poro)
    profile = _fill_properties(profile, poro)
    profile = _fill_events(profile, events, logger)
    profile = _normalize_profile(profile)
    return profile


async def _calc_injection(
    well: UneftWellDB,
    profile: pd.DataFrame,
    dao: FnvReporter,
    logger: logging.Logger,
) -> pd.DataFrame:
    logger.info("-" * 160)
    logger.info(
        "Создан профиль долей закачки: %s (%s - %s)",
        well.uwi,
        profile["MD"].min() / 100,
        profile["MD"].max() / 100,
    )
    logger.info("-" * 160)
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
            well.uwi, profile.columns[index], profile.columns[index + 1]
        )
        # профиль притока по интервалу = доля закачки * на закачку
        profile[current] = profile[current] * totwat
        # сделать список названий пластов с непустым притоком в log_df
        log_df = profile[profile[current] != 0]["layer_name"].unique()
        logger.info(
            "%s Закачка (%s - %s) : %.0f, по профилю : %.0f %s",
            well.uwi,
            profile.columns[index],
            profile.columns[index + 1],
            totwat,
            profile[current].sum(),
            log_df,
        )
    # суммируем столбцы, начиная с 5-го
    profile["total"] = profile.iloc[:, i_start_col:].sum(axis=1)
    # вывести строки с непустым названием пласта и непустым последним столбцом
    logger.info("-" * 160)
    logger.info(
        "%s Всего закачка по профилям: %s", well.uwi, profile["total"].sum()
    )
    logger.debug(
        "Ненулевые профили закачки:\n%s",
        profile[(profile["layer_name"] != "") & (profile.iloc[:, -1] > 0)],
    )
    return profile


def _calc_radius(
    well: UneftWellDB, profile: pd.DataFrame, logger: logging.Logger
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
    logger.info("-" * 160)
    logger.info("%s Радиусы ФНВ по пластам:", well.uwi)
    logger.info("\n%s", layers_radius)
    return layers_radius


def _calc_contours(
    well: UneftWellDB,
    layers_radius: pd.DataFrame,
    min_radius: float,
    logger: logging.Logger,
) -> pd.DataFrame:
    result = pd.DataFrame(columns=["contour"], index=layers_radius.index)
    logger.info("-" * 160)
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
            logger.info(
                "%s Круг для %s : (%s - %s) R = %s", well.uwi, index, x, y, r
            )
        result.loc[index, "contour"] = contour  # type:ignore
    result.columns = [well.uwi]  # type:ignore
    return result


async def _calc_profile(
    well: UneftWellDB,
    poro: pd.DataFrame,
    events: pd.DataFrame,
    min_radius: float,
    dao: FnvReporter,
    logger: logging.Logger,
) -> pd.DataFrame:
    profile = _get_profile(poro, events, logger)
    profile = await _calc_injection(well, profile, dao, logger)
    layers_radius = _calc_radius(well, profile, logger)
    contours = _calc_contours(well, layers_radius, min_radius, logger)
    return contours


async def _process_well(
    well: UneftWellDB,
    min_radius: float,
    alternative: bool,
    dao: FnvReporter,
    logger: logging.Logger,
) -> pd.DataFrame:
    logger.info("-" * 160)
    logger.info(">>> Скважина: %s", well.uwi)
    poro = await dao.poro(well.uwi)
    logger.info("Пористость: %s", well.uwi)
    if not poro.size:
        raise FnvException("нет пористости")
    logger.info("\n%s", poro)
    events = await dao.events(alternative, well.uwi)
    logger.info("События: %s", well.uwi)
    contours = await _calc_profile(well, poro, events, min_radius, dao, logger)
    logger.info("%s Созданы контуры ФНВ", well.uwi)
    logger.debug("%s", contours)
    return contours


async def _make_contours(
    field: UneftFieldDB,
    min_radius: float,
    alternative: bool,
    wells: list[UneftWellDB],
    dao: FnvReporter,
    logger: logging.Logger,
) -> pd.DataFrame:
    final_contours = await dao.layers(field.id)
    final_contours = final_contours.groupby(["cid", "layer_name"]).agg("first")
    for well in wells:
        try:
            contours = await _process_well(
                well, min_radius, alternative, dao, logger
            )
            final_contours = pd.merge(
                final_contours,
                contours,
                how="left",
                left_index=True,
                right_index=True,
            )
        except FnvException as error:
            logger.error(
                "Не обработана скважина: %s : %s",
                well.uwi,
                error,
                exc_info=True,
            )
    final_contours.fillna(0, inplace=True)
    logger.info("-" * 160)
    logger.info(
        "%s: cкважин с профилями: %s",
        field.name,
        final_contours.columns.size,
    )
    logger.debug("%s", final_contours)
    return final_contours


async def _save_countours(
    path: Path, contours: pd.DataFrame, logger: logging.Logger
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
    logger.info("-" * 160)
    logger.warning("Сохранено в %s", path)


async def fnv_report(
    path: Path,
    field: UneftFieldDB,
    min_radius: float,
    alternative: bool,
    wells: list[UneftWellDB],
    dao: FnvReporter,
    pool: ProcessPoolManager,
) -> None:
    try:
        result_path = path / field.name
        result_path.mkdir(parents=True, exist_ok=True)
        logger = _configure_logging(str(path), result_path)
        logger.warning("Start")
        logger.warning("Field = %s", field.name)
        logger.warning("Min radius = %s", min_radius)
        logger.warning("Alternative = %s", alternative)
        logger.warning("Скважин в ППД: %s", len(wells))
        contours = await _make_contours(
            field, min_radius, alternative, wells, dao, logger
        )
        await _save_countours(result_path, contours, logger)
        make_archive(str(path), "zip", root_dir=path)
        logger.warning("Finish")
    finally:
        logging.root.manager.loggerDict.pop(str(path), None)
