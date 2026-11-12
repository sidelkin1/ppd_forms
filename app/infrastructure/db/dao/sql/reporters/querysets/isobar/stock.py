from typing import Any

from sqlalchemy import (
    Date,
    Integer,
    and_,
    bindparam,
    case,
    cast,
    func,
    literal,
    null,
    select,
    union_all,
)
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select
from sqlalchemy.sql.selectable import Subquery

from app.core.models.enums import IsobarStatus
from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    Reservoir2,
    ResPty,
    TmpWellNgOis2,
    TmpWellOpOis2,
    WellHdr,
    WellPerforations,
    WellStockHist,
    WellStockHistExt,
)

from .common import base_reservoir_id, cid_column

_SLOTS = ("1", "2", "3")
_STOCK_COLUMNS = (
    "field",
    "uwi",
    "well_name",
    "parent",
    "reservoir",
    "cid",
    "type_",
    "status",
    "p_init",
    "p_bubble",
)


def _select_open_wellbores() -> Subquery:
    """Стволы с открытой на дату отчёта перфорацией.

    Берутся все такие тройки «скважина, базовый объект, ствол»: часть из
    них уже есть в фонде (тогда даёт историю), остальные добавятся со
    состоянием «открыт. перф.» — в фонде ОФМ их почему-то нет, хотя
    перфорация открыта.
    """
    branch = aliased(WellHdr)
    return (
        select(
            func.coalesce(branch.parent_uwi, branch.uwi).label("uwi"),
            base_reservoir_id().label("reservoir_id"),
            branch.uwi.label("bs_uwi"),
        )
        .select_from(WellPerforations)
        .join(branch, branch.uwi == WellPerforations.uwi)
        .join(DictG, DictG.id == WellPerforations.layer_id)
        .where(
            WellPerforations.comp_date <= bindparam("on_date"),
            WellPerforations.close_date.is_(None)
            | (WellPerforations.close_date >= bindparam("on_date")),
        )
        .distinct()
        .subquery("open_wellbores")
    )


def _select_wellbores() -> Subquery:
    """Стволы фонда: текущие, прежние и с открытой перфорацией.

    По каждой тройке «скважина, объект работы, ствол» берём последнюю
    дату: она равна дате фонда у текущего ствола и более ранняя у прежних.
    Объект резолвится к базовому (``mr`` → id), иначе смена объекта на
    ИЖВ и обратно давала бы лишние прежние стволы.

    К истории добавляются стволы с открытой на дату отчёта перфорацией,
    которых в фонде нет: у них нет последней даты, состояние
    «открыт. перф.» (``open_perf = 1``). Дубли снимаются группировкой:
    если ствол есть в истории, берётся её дата, а ``open_perf`` остаётся 1.

    ``current_reservoir_id`` — исходный ``ora{n}`` на дату фонда: он нужен
    только для склейки с техрежимом (там объект хранится текстом) и в
    итоговый фонд не попадает.
    """
    stock_date: Any = bindparam("stock_date")
    parts = []
    for slot in _SLOTS:
        reservoir = getattr(WellStockHistExt, f"ora{slot}")
        wellbore = getattr(WellStockHistExt, f"bs{slot}")
        parts.append(
            select(
                WellStockHistExt.uwi.label("uwi"),
                base_reservoir_id().label("reservoir_id"),
                wellbore.label("bs_uwi"),
                WellStockHistExt.status_date.label("status_date"),
                case(
                    (WellStockHistExt.status_date == stock_date, reservoir)
                ).label("current_reservoir_id"),
            )
            .select_from(WellStockHistExt)
            .join(DictG, DictG.id == reservoir)
            .where(
                WellStockHistExt.status_date <= stock_date,
                wellbore.is_not(None),
                reservoir.is_not(None),
            )
        )
    history = union_all(*parts).subquery("history")
    opened_wellbores = _select_open_wellbores()
    grouped = select(
        history.c.uwi,
        history.c.reservoir_id,
        history.c.bs_uwi,
        func.max(history.c.status_date).label("last_date"),
        func.max(history.c.current_reservoir_id).label("current_reservoir_id"),
        literal(0).label("open_perf"),
    ).group_by(history.c.uwi, history.c.reservoir_id, history.c.bs_uwi)
    opened = select(
        opened_wellbores.c.uwi,
        opened_wellbores.c.reservoir_id,
        opened_wellbores.c.bs_uwi,
        cast(null(), Date).label("last_date"),
        cast(null(), Integer).label("current_reservoir_id"),
        literal(1).label("open_perf"),
    ).select_from(opened_wellbores)
    combined = union_all(grouped, opened).subquery("combined")
    return (
        select(
            combined.c.uwi,
            combined.c.reservoir_id,
            combined.c.bs_uwi,
            func.max(combined.c.last_date).label("last_date"),
            func.max(combined.c.current_reservoir_id).label(
                "current_reservoir_id"
            ),
            func.max(combined.c.open_perf).label("open_perf"),
        )
        .group_by(combined.c.uwi, combined.c.reservoir_id, combined.c.bs_uwi)
        .subquery("wellbores")
    )


def _select_stock() -> Select:
    """Текущий фонд и прежние стволы тех же объектов одной выборкой.

    Признак текущего ствола — последняя дата, совпадающая с датой фонда.
    Справочники и PVT подключаются через LEFT JOIN: объект мог уйти из
    актуального справочника, и тогда строка остаётся без PVT-свойств.
    """
    wellbores = _select_wellbores()
    reservoir = func.udmurtneft_n.dg_des(wellbores.c.reservoir_id)
    # «открыт. перф.» — ствол, которого нет в фонде, но перфорация открыта
    is_current = wellbores.c.last_date == bindparam("stock_date")
    has_open_perf = wellbores.c.open_perf == 1
    branch = aliased(WellHdr)
    parent = aliased(WellHdr)
    return (
        select(
            func.udmurtneft_n.dg_des(WellHdr.field).label("field"),
            func.coalesce(WellHdr.parent_uwi, WellHdr.uwi).label("uwi"),
            branch.well_name.label("well_name"),
            parent.well_name.label("parent"),
            reservoir.label("reservoir"),
            cid_column().label("cid"),
            wellbores.c.reservoir_id.label("reservoir_id"),
            wellbores.c.current_reservoir_id.label("current_reservoir_id"),
            func.udmurtneft_n.dg_sdes(WellStockHist.prod_class).label("type_"),
            case(
                (
                    is_current,
                    func.udmurtneft_n.dg_sdes(WellStockHist.status),
                ),
                (has_open_perf, literal(IsobarStatus.open_perf.value)),
                else_=literal(IsobarStatus.old_wellbore.value),
            ).label("status"),
            ResPty.initial_layer_pressure.label("p_init"),
            ResPty.bubble_point_pressure.label("p_bubble"),
        )
        .select_from(wellbores)
        .join(branch, branch.uwi == wellbores.c.bs_uwi)
        .join(WellHdr, WellHdr.uwi == wellbores.c.uwi)
        .join(
            parent,
            parent.uwi == func.coalesce(WellHdr.parent_uwi, WellHdr.uwi),
        )
        .outerjoin(
            WellStockHist,
            and_(
                WellStockHist.uwi == wellbores.c.uwi,
                # у ствола с открытой перфорацией своей даты нет — берём
                # характер работы из текущего состояния скважины
                WellStockHist.status_date
                == func.coalesce(
                    wellbores.c.last_date, bindparam("stock_date")
                ),
            ),
        )
        .outerjoin(
            Reservoir2,
            and_(
                Reservoir2.reservoir_id == wellbores.c.reservoir_id,
                Reservoir2.field_code == WellHdr.field,
                Reservoir2.district == WellHdr.district,
                Reservoir2.existence_type == "ACTUAL",
            ),
        )
        .outerjoin(ResPty, ResPty.reservoir_s == Reservoir2.reservoir_s)
        .outerjoin(DictG, DictG.id == wellbores.c.reservoir_id)
    )


def _select_tmp_pressures() -> Subquery:
    """Давления техрежима, по строке на скважину и объект работы.

    WELLOP приоритетнее WELLNG. Предварительная агрегация нужна, чтобы
    Oracle выбрал hash join: join фонда к сырым TMP-таблицам идёт ~10 с.
    """
    wellop = select(
        TmpWellOpOis2.uwi.label("uwi"),
        func.lower(TmpWellOpOis2.layer_id).label("layer_id"),
        TmpWellOpOis2.shut_pressure.label("shut"),
        TmpWellOpOis2.flow_pressure.label("flow"),
        literal(0).label("src"),
    ).where(TmpWellOpOis2.official_date == bindparam("on_date"))
    wellng = select(
        TmpWellNgOis2.uwi.label("uwi"),
        func.lower(TmpWellNgOis2.layer_id).label("layer_id"),
        TmpWellNgOis2.layer_shut_pressure.label("shut"),
        TmpWellNgOis2.layer_flow_pressure.label("flow"),
        literal(1).label("src"),
    ).where(TmpWellNgOis2.official_date == bindparam("on_date"))
    tmp = union_all(wellop, wellng).subquery("tmp")
    return (
        select(
            tmp.c.uwi,
            tmp.c.layer_id,
            func.coalesce(
                func.max(case((tmp.c.src == 0, tmp.c.shut))),
                func.max(case((tmp.c.src == 1, tmp.c.shut))),
            ).label("p_tr"),
            func.coalesce(
                func.max(case((tmp.c.src == 0, tmp.c.flow))),
                func.max(case((tmp.c.src == 1, tmp.c.flow))),
            ).label("p_bhp"),
        )
        .group_by(tmp.c.uwi, tmp.c.layer_id)
        .subquery("tmp_pressures")
    )


def select_stock() -> Select:
    """Фонд со всеми стволами объектов, PVT-свойства и давления.

    В фонд входят текущие стволы объектов, все прежние («стар. ствол») и
    стволы с открытой перфорацией, которых в фонде нет («открыт. перф.»).
    """
    stock = _select_stock().subquery("stock")
    stock_keys = select(
        *(stock.c[column] for column in _STOCK_COLUMNS),
        func.lower(
            func.udmurtneft_n.dg_des(stock.c.current_reservoir_id)
        ).label("reservoir_lower"),
    ).subquery("stock_keys")
    pressures = _select_tmp_pressures()
    # техрежим склеивается только с текущими стволами: у прежних стволов
    # и стволов с открытой перфорацией case ниже оставляет p_tr и p_bhp
    # пустыми (NULL). Склейка идёт по исходному ora на дату фонда —
    # техрежим хранит объект текстом, и это описание совпадает с ним.
    is_current = ~func.coalesce(stock_keys.c.status, "").in_(
        (IsobarStatus.old_wellbore.value, IsobarStatus.open_perf.value)
    )
    return (
        select(
            *(stock_keys.c[column] for column in _STOCK_COLUMNS),
            case((is_current, pressures.c.p_tr)).label("p_tr"),
            case((is_current, pressures.c.p_bhp)).label("p_bhp"),
        )
        .select_from(stock_keys)
        .outerjoin(
            pressures,
            and_(
                stock_keys.c.uwi == pressures.c.uwi,
                stock_keys.c.reservoir_lower == pressures.c.layer_id,
            ),
        )
        # Reservoir2/ResPty подключаются через LEFT JOIN и при нескольких
        # совпадениях дают дубли строк (как в pvt_props.py).
        .distinct()
    )
