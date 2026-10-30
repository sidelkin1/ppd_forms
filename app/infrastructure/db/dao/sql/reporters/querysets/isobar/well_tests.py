from collections.abc import Sequence
from datetime import date

from sqlalchemy import (
    Date,
    String,
    and_,
    bindparam,
    column,
    func,
    or_,
    select,
    values,
)
from sqlalchemy.sql.expression import ColumnElement, Select

from app.infrastructure.db.models.local import WellTest

FAILED_CURATOR = "Неуспешная"

PREV_COLUMNS = (
    "field",
    "well",
    "end_date",
    "reservoir",
    "well_type",
    "well_status",
)

_SUCCEEDED = or_(
    WellTest.curator.is_(None), WellTest.curator != FAILED_CURATOR
)
_FAILED = WellTest.curator == FAILED_CURATOR


def _select_last_tests(
    curator_condition: ColumnElement[bool], *conditions: ColumnElement[bool]
) -> Select:
    """Последний замер по каждому ключу из заданного окна."""
    row_number = (
        func.row_number()
        .over(
            partition_by=(WellTest.field, WellTest.well, WellTest.reservoir),
            order_by=(WellTest.end_date.desc(), WellTest.well_test),
        )
        .label("rn")
    )
    subq = (
        select(
            WellTest.field,
            WellTest.well,
            WellTest.reservoir,
            WellTest.well_test,
            WellTest.end_date,
            WellTest.resp_owc,
            row_number,
        )
        .where(
            WellTest.resp_owc.is_not(None),
            curator_condition,
            *conditions,
        )
        .subquery()
    )
    return select(
        subq.c.field,
        subq.c.well,
        subq.c.reservoir,
        subq.c.well_test,
        subq.c.end_date,
        subq.c.resp_owc,
    ).where(subq.c.rn == 1)


def select_succeeded_tests() -> Select:
    """Последний успешный замер за квартал [date_from, date_to)."""
    return _select_last_tests(
        _SUCCEEDED,
        WellTest.end_date >= bindparam("date_from"),
        WellTest.end_date < bindparam("date_to"),
    )


def select_failed_tests() -> Select:
    """Последний неуспешный замер за квартал [date_from, date_to)."""
    return _select_last_tests(
        _FAILED,
        WellTest.end_date >= bindparam("date_from"),
        WellTest.end_date < bindparam("date_to"),
    )


def select_previous_tests(
    rows: Sequence[tuple[str, str, date, str]],
) -> Select:
    """Тип и состояние скважины на даты предыдущих замеров.

    ``rows`` — уникальные четвёрки (месторождение, скважина без ствола,
    дата замера, объект работы ``cid``). Вместо строкового ключа
    используется CTE ``requested`` (``VALUES``) с join по типизированным
    колонкам: планировщик может применить индексы `welltest`.

    ``well_test`` в ключ не входит: «вид исследования» в сводной и
    ``welltest.well_test`` — разные справочники (совпадает ~46% значений).
    Если на одну дату по объекту несколько замеров, порядок выборки
    детерминирован (``order_by(WellTest.well_test)``), а тип и состояние —
    скважинные атрибуты, поэтому конкретный замер не важен.
    """
    requested = values(
        column("field", String),
        column("well", String),
        column("end_date", Date),
        column("reservoir", String),
        name="requested",
    ).data(rows)
    return (
        select(
            requested.c.field,
            requested.c.well,
            requested.c.end_date,
            requested.c.reservoir,
            WellTest.well_type,
            WellTest.well_status,
        )
        .select_from(requested)
        .join(
            WellTest,
            and_(
                WellTest.field == requested.c.field,
                WellTest.well == requested.c.well,
                WellTest.end_date == requested.c.end_date,
                WellTest.reservoir == requested.c.reservoir,
            ),
        )
        .order_by(WellTest.well_test)
    )
