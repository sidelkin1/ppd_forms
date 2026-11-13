"""Проверки целостности и диагностика расхождений сводной."""

from datetime import date
from pathlib import Path

import pandas as pd

from .columns import (
    LOST_COLUMNS,
    LOST_HEADERS,
    LOST_TESTS_HEADERS,
    MISS_HEADERS,
    OUTPUT_PREFIX,
    STATE_HEADERS,
)
from .preparation import to_date


def _unmatched_tests(tests: pd.DataFrame, stock: pd.DataFrame) -> pd.DataFrame:
    """Замеры с Рпл, для которых в фонде нет строки ствола.

    ``tests`` — успешные и неуспешные замеры с колонкой ``curator``:
    в файле видно, как оценён замер.
    """
    if tests.empty or stock.empty:
        return pd.DataFrame(columns=[*LOST_COLUMNS, "curator"])
    keys = (
        stock[["field", "well_name", "cid"]]
        .drop_duplicates()
        .rename(columns={"well_name": "branch", "cid": "reservoir"})
    )
    checked = tests.merge(
        keys, on=["field", "branch", "reservoir"], how="left", indicator=True
    )
    unmatched = checked[checked["_merge"] == "left_only"]
    return (
        pd.DataFrame(
            {
                "field": unmatched["field"],
                "well": unmatched["branch"],
                "reservoir": unmatched["reservoir"],
                "well_test": unmatched["well_test"],
                "resp": unmatched["resp_owc"].round(2),
                "end_date": unmatched["end_date"],
                "curator": unmatched["curator"],
            }
        )
        .sort_values(list(LOST_COLUMNS))
        .reset_index(drop=True)
    )


def _unmatched_previous(
    prev_values: pd.DataFrame, stock: pd.DataFrame
) -> pd.DataFrame:
    """Строки предыдущей сводной с Рпл, которым нет пары в фонде."""
    if prev_values.empty or stock.empty:
        return pd.DataFrame(columns=list(LOST_COLUMNS))
    values = prev_values[prev_values["prev_resp"].notna()]
    keys = (
        stock[["field", "well_name", "cid"]]
        .drop_duplicates()
        .rename(columns={"well_name": "well", "cid": "reservoir"})
    )
    checked = values.merge(
        keys, on=["field", "well", "reservoir"], how="left", indicator=True
    )
    unmatched = checked[checked["_merge"] == "left_only"]
    return (
        pd.DataFrame(
            {
                "field": unmatched["field"],
                "well": unmatched["well"],
                "reservoir": unmatched["reservoir"],
                "well_test": unmatched["prev_well_test"],
                "resp": unmatched["prev_resp"].round(2),
                "end_date": unmatched["prev_date"],
            }
        )
        .sort_values(list(LOST_COLUMNS))
        .reset_index(drop=True)
    )


def _previous_info(prev_values: pd.DataFrame) -> pd.DataFrame:
    """Вид исследования и Рпл из строки предыдущей сводной."""
    info = pd.DataFrame(
        {
            "field": prev_values["field"],
            "well": prev_values["well_nb"],
            "end_date": prev_values["prev_date"],
            "reservoir": prev_values["reservoir"],
            "well_test": prev_values["prev_well_test"],
            "resp": prev_values["prev_resp"],
        }
    )
    return info.drop_duplicates(
        subset=["field", "well", "end_date", "reservoir"], keep="first"
    )


def _missing_state_keys(
    prev_values: pd.DataFrame,
    found: pd.DataFrame,
) -> pd.DataFrame:
    """Замеры предыдущей сводной, которых нет в welltest.

    Ключ замера — месторождение, скважина, дата замера, объект; берётся из
    самой предыдущей сводной. Для таких замеров в колонках M/N сводной не
    будет типа и состояния скважины.
    """
    columns = ["field", "well", "end_date", "reservoir"]
    if prev_values.empty:
        return pd.DataFrame(columns=columns)
    requested = (
        prev_values[["field", "well_nb", "prev_date", "reservoir"]]
        # правило как в DAO при чтении состояний: поле не бывает пустым
        .dropna(subset=["well_nb", "prev_date", "reservoir"])
        .rename(columns={"well_nb": "well", "prev_date": "end_date"})
        .drop_duplicates()
    )
    requested["end_date"] = to_date(requested["end_date"])
    found = found[columns].drop_duplicates()
    found["end_date"] = to_date(found["end_date"])
    checked = requested.merge(found, on=columns, how="left", indicator=True)
    missing = checked[checked["_merge"] == "left_only"][columns]
    if missing.empty:
        return missing
    return missing.merge(
        _previous_info(prev_values),
        on=columns,
        how="left",
        validate="many_to_one",
    )


def _previous_misses(
    stock: pd.DataFrame, prev_values: pd.DataFrame
) -> pd.DataFrame:
    """Объекты фонда, для которых в предыдущей сводной нет строки."""
    columns = ["field", "well_name", "cid", "file_reservoir"]
    if prev_values.empty:
        return pd.DataFrame(columns=columns)
    file_keys = prev_values[["field", "well", "reservoir"]].drop_duplicates()
    file_wells = file_keys[["field", "well"]].drop_duplicates()
    stock_keys = stock[["field", "well_name", "cid"]].drop_duplicates()
    candidates = stock_keys.merge(
        file_wells,
        left_on=["field", "well_name"],
        right_on=["field", "well"],
    )
    check = candidates.merge(
        file_keys,
        left_on=["field", "well_name", "cid"],
        right_on=["field", "well", "reservoir"],
        how="left",
        indicator=True,
    )
    missed = check[check["_merge"] == "left_only"].drop_duplicates(
        subset=["field", "well_name", "cid"]
    )
    file_by_well = (
        file_keys.groupby(["field", "well"])["reservoir"]
        .agg(lambda values: ", ".join(sorted(map(str, values))))
        .to_dict()
    )
    missed = missed.assign(
        file_reservoir=[
            file_by_well.get((field, well), "")
            for field, well in zip(missed["field"], missed["well_name"])
        ]
    )
    return missed[columns].reset_index(drop=True)


def _write_misses(
    path: Path, on_date: date, missed: pd.DataFrame
) -> str | None:
    """Пишет объекты фонда, которых нет в предыдущей сводной."""
    if missed.empty:
        return None
    name = f"{OUTPUT_PREFIX}_{on_date:%d.%m.%Y}_нет_строки_в_сводной.csv"
    missed.rename(columns=MISS_HEADERS, errors="raise").to_csv(
        path / name, index=False, sep=";", encoding="utf-8-sig"
    )
    return (
        f"Изобары: для {len(missed)} объектов фонда нет строки в "
        f"предыдущей сводной — полный список в файле «{name}»"
    )


def _write_state_misses(
    path: Path, on_date: date, missing: pd.DataFrame
) -> str | None:
    """Пишет замеры предыдущей сводной, которых нет в welltest.

    Ключ замера — месторождение, скважина, дата замера, объект; по нему
    в welltest берутся тип и состояние скважины для колонок M/N.
    """
    if missing.empty:
        return None
    name = f"{OUTPUT_PREFIX}_{on_date:%d.%m.%Y}_нет_данных_гдис.csv"
    missing.rename(columns=STATE_HEADERS, errors="raise").to_csv(
        path / name, index=False, sep=";", encoding="utf-8-sig"
    )
    return (
        f"Изобары: для {len(missing)} ключей предыдущей сводной нет "
        f"записей в welltest (M/N не заполнены) — полный список в файле "
        f"«{name}»"
    )


def _write_lost_values(
    path: Path,
    on_date: date,
    missing: pd.DataFrame,
    suffix: str,
    source: str,
    headers: dict[str, str],
) -> str | None:
    """Пишет Рпл, которому не нашлось пары в фонде.

    Рпл приходит из двух мест: из предыдущей сводной и из текущих замеров
    welltest; ``source`` — название источника для сообщения («предыдущей
    сводной», «текущих замеров»), ``suffix`` — часть имени файла,
    ``headers`` — русские заголовки колонок этого источника.
    """
    if missing.empty:
        return None
    name = f"{OUTPUT_PREFIX}_{on_date:%d.%m.%Y}_{suffix}.csv"
    missing.rename(columns=headers, errors="raise").to_csv(
        path / name, index=False, sep=";", encoding="utf-8-sig"
    )
    return (
        f"Изобары: {len(missing)} строк {source} с Рпл не попали в фонд — "
        f"полный список в файле «{name}»"
    )


def _write_branch_fallbacks(
    path: Path, on_date: date, fallbacks: pd.DataFrame
) -> str | None:
    """Пишет замеры, для которых не нашлось ни одной открытой перфорации.

    В сводной у них стволом остаётся номер скважины без ствола.
    """
    if fallbacks.empty:
        return None
    name = f"{OUTPUT_PREFIX}_{on_date:%d.%m.%Y}_ствол_не_определен.csv"
    fallbacks.rename(columns=LOST_HEADERS, errors="raise").to_csv(
        path / name, index=False, sep=";", encoding="utf-8-sig"
    )
    return (
        f"Изобары: у {len(fallbacks)} замеров не найдена открытая "
        f"перфорация, ствол не определён — полный список в файле «{name}»"
    )


def write_diagnostics(
    *,
    path: Path,
    on_date: date,
    dfs: dict[str, pd.DataFrame],
    fallbacks: pd.DataFrame,
) -> list[str]:
    """Пишет файлы диагностики, возвращает сообщения для лога.

    Выполняется в воркере; предупреждения пишет сервис — готовыми
    сообщениями, без повторной сборки текста.
    """
    messages = (
        _write_branch_fallbacks(path, on_date, fallbacks),
        _write_state_misses(
            path,
            on_date,
            _missing_state_keys(dfs["prev_values"], dfs["prev_state"]),
        ),
        _write_lost_values(
            path,
            on_date,
            _unmatched_previous(dfs["prev_values"], dfs["stock"]),
            "нет_в_фонде_сводная",
            "предыдущей сводной",
            LOST_HEADERS,
        ),
        _write_lost_values(
            path,
            on_date,
            _unmatched_tests(
                pd.concat(
                    [dfs["succeeded"], dfs["failed"]], ignore_index=True
                ),
                dfs["stock"],
            ),
            "нет_в_фонде_welltest",
            "текущих замеров",
            LOST_TESTS_HEADERS,
        ),
        # строки фонда и отчёта совпадают: prepare_dataframe только
        # добавляет колонки левыми склейками, без изменения числа строк
        _write_misses(
            path,
            on_date,
            _previous_misses(dfs["stock"], dfs["prev_values"]),
        ),
    )
    return [message for message in messages if message]
