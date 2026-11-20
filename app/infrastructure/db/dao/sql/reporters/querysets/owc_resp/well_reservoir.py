from sqlalchemy import (
    bindparam,
    func,
    literal,
    select,
    union_all,
)
from sqlalchemy.sql.expression import ScalarSelect

from app.infrastructure.db.models.ofm.udmurtneft_n import WellStockHistExt

from .branches import select_well_branch
from .reservoirs import select_reservoir_ids


def select_well_reservoir_id() -> ScalarSelect:
    """`layer_id` выбранного ствола в кодировке месторождения.

    Ствол — результат `select_well_branch()`: ствол с открытой на дату
    перфорацией в целевом объекте либо родительский. Из истории фонда
    разворачиваются `ora1..3`; оставляются только значения, входящие в
    `select_reservoir_ids()` (базовый объект и его `DictG.mr`-псевдонимы),
    и только слоты, чей `bsN` указывает на выбранный ствол. Из них берётся
    самая поздняя запись.

    Порядок важен: сначала фильтр по объекту, потом выбор даты. Иначе
    более поздняя запись о другом объекте скрывала бы нужную историю.

    При равной дате — слоты 1, 2, 3. `ROW_NUMBER` гарантирует ровно
    одну строку (или NULL, если совпадений нет).
    """
    branch = select_well_branch().scalar_subquery()
    parts = []
    for slot in (1, 2, 3):
        ora = getattr(WellStockHistExt, f"ora{slot}")
        bs = getattr(WellStockHistExt, f"bs{slot}")
        parts.append(
            select(
                WellStockHistExt.status_date.label("status_date"),
                literal(slot).label("slot"),
                ora.label("layer_id"),
            ).where(
                WellStockHistExt.status_date <= bindparam("on_date"),
                ora.is_not(None),
                ora.in_(select_reservoir_ids()),
                bs == branch,
            )
        )
    candidates = union_all(*parts).subquery("owc_layer_candidates")
    ranked = select(
        candidates.c.layer_id,
        func.row_number()
        .over(
            order_by=(
                candidates.c.status_date.desc(),
                candidates.c.slot,
            )
        )
        .label("rn"),
    ).subquery("owc_layer_ranked")
    return select(ranked.c.layer_id).where(ranked.c.rn == 1).scalar_subquery()
