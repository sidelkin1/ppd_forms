from sqlalchemy import func, select
from sqlalchemy.sql.expression import ScalarSelect, SQLColumnExpression

from app.infrastructure.db.models.ofm.codes import DictG


def select_cid_no_license(cid: SQLColumnExpression[str]) -> ScalarSelect:
    return (
        select(
            func.udmurtneft_n.dg_sdes(
                func.min(func.decode(DictG.mr, None, DictG.id, DictG.mr))
            )
        )
        .where(DictG.sdes == cid)
        .correlate_except(DictG)
    ).scalar_subquery()


def select_uniqueid_no_license(
    uniqueid: SQLColumnExpression[str],
) -> ScalarSelect:
    well = func.substr(uniqueid, 1, func.instr(uniqueid, ":") - 1)
    cid = func.substr(uniqueid, func.instr(uniqueid, ":") + 1)
    return (
        select(well + ":" + select_cid_no_license(cid))
        .correlate_except(DictG)
        .scalar_subquery()
    )
