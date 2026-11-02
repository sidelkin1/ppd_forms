from sqlalchemy import (
    and_,
    bindparam,
    case,
    func,
    literal,
    select,
    union_all,
)
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select
from sqlalchemy.sql.selectable import Subquery

from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    Reservoir2,
    ResPty,
    TmpWellNgOis2,
    TmpWellOpOis2,
    WellHdr,
    WellStockHist,
    WellStockHistExt,
)

_SLOTS = ("1", "2", "3")
_OLD_WELLBORE_STATUS = "стар. ствол"
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


def _select_wellbores() -> Subquery:
    """Стволы, работавшие на объектах, с последней датой на дату фонда.

    По каждой тройке «скважина, объект работы, ствол» берём последнюю
    дату: она равна дате фонда у текущего ствола и более ранняя у прежних.
    """
    parts = []
    for slot in _SLOTS:
        reservoir = getattr(WellStockHistExt, f"ora{slot}")
        wellbore = getattr(WellStockHistExt, f"bs{slot}")
        parts.append(
            select(
                WellStockHistExt.uwi.label("uwi"),
                reservoir.label("reservoir_id"),
                wellbore.label("bs_uwi"),
                WellStockHistExt.status_date.label("status_date"),
            ).where(
                WellStockHistExt.status_date <= bindparam("stock_date"),
                wellbore.is_not(None),
                reservoir.is_not(None),
            )
        )
    history = union_all(*parts).subquery("history")
    return (
        select(
            history.c.uwi,
            history.c.reservoir_id,
            history.c.bs_uwi,
            func.max(history.c.status_date).label("last_date"),
        )
        .group_by(history.c.uwi, history.c.reservoir_id, history.c.bs_uwi)
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
    is_current = wellbores.c.last_date == bindparam("stock_date")
    branch = aliased(WellHdr)
    parent = aliased(WellHdr)
    return (
        select(
            func.udmurtneft_n.dg_des(WellHdr.field).label("field"),
            func.coalesce(WellHdr.parent_uwi, WellHdr.uwi).label("uwi"),
            branch.well_name.label("well_name"),
            parent.well_name.label("parent"),
            reservoir.label("reservoir"),
            # суффикс "(Руд)" есть только в OFM: в локальной БД и в
            # предыдущей сводной объект хранится без него
            func.replace(
                func.udmurtneft_n.dg_sdes(
                    func.decode(DictG.mr, None, DictG.id, DictG.mr)
                ),
                "(Руд)",
            ).label("cid"),
            func.udmurtneft_n.dg_sdes(WellStockHist.prod_class).label("type_"),
            case(
                (is_current, func.udmurtneft_n.dg_sdes(WellStockHist.status)),
                else_=literal(_OLD_WELLBORE_STATUS),
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
                WellStockHist.status_date == wellbores.c.last_date,
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

    В фонд входят не только текущие стволы объектов, но и все прежние
    стволы, которые на этих объектах были (состояние «стар. ствол»).
    """
    stock = _select_stock().subquery("stock")
    stock_keys = select(
        *(stock.c[column] for column in _STOCK_COLUMNS),
        func.lower(stock.c.reservoir).label("reservoir_lower"),
    ).subquery("stock_keys")
    pressures = _select_tmp_pressures()
    # давления техрежима относятся только к текущим стволам: у прежних
    # стволов ячейки остаются пустыми
    is_current = func.coalesce(stock_keys.c.status, "") != _OLD_WELLBORE_STATUS
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
    )
