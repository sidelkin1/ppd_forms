from sqlalchemy import (
    CompoundSelect,
    Select,
    bindparam,
    literal_column,
    select,
    union_all,
)

from app.infrastructure.db.models.ofm.reflected import (
    GeophysSt,
    GeophysStAbsorp,
    HeaderId,
    Perf,
    PerfAlt,
)


def _select_perf() -> Select:
    return select(
        Perf.date_op,
        Perf.type_action,
        Perf.top,
        Perf.base,
        literal_column("0").label("prof"),
    ).where(Perf.uwi == bindparam("uwi"))


def _select_perf_alt() -> Select:
    return select(
        PerfAlt.date_op,
        PerfAlt.type_action,
        PerfAlt.top,
        PerfAlt.base,
        literal_column("0").label("prof"),
    ).where(PerfAlt.uwi == bindparam("uwi"))


def _select_geophys() -> Select:
    return (
        select(
            GeophysSt.rec_date.label("date_op"),
            literal_column("'GDI'").label("type_action"),
            GeophysStAbsorp.top,
            GeophysStAbsorp.bottom.label("base"),
            GeophysStAbsorp.diff_absorp.label("prof"),
        )
        .join(GeophysSt, GeophysSt.id == GeophysStAbsorp.id)
        .join(HeaderId, HeaderId.uwi == GeophysSt.uwi)
        .where(
            HeaderId.uwi == bindparam("uwi"),
            GeophysStAbsorp.diff_absorp.is_not(None),
        )
        .distinct()
    )


def select_events() -> CompoundSelect:
    return union_all(_select_perf(), _select_geophys()).order_by("date_op")


def select_events_alt() -> CompoundSelect:
    return union_all(_select_perf_alt(), _select_geophys()).order_by("date_op")
