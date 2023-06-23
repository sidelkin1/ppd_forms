import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.local_db import get_async_session
from app.models.monthly_report import MonthlyReport
from app.models.well_profile import WellProfile
from app.schemas.database import DateRange

router = APIRouter()


@router.post('/data')
async def get_data(
    update: DateRange,
    session: AsyncSession = Depends(get_async_session),
):
    subq_absorp = select(
        WellProfile.uwi,
        WellProfile.cid_all,
        WellProfile.rec_date,
        func.sum(WellProfile.diff_absorp).label('total_absorp'),
    ).group_by(
        WellProfile.uwi,
        WellProfile.cid_all,
        WellProfile.rec_date,
    ).subquery()

    subq_rec_date = select(
        subq_absorp.c.uwi,
        subq_absorp.c.cid_all,
        func.max(subq_absorp.c.rec_date).label('max_date')
    ).where(
        subq_absorp.c.total_absorp > 0,
    ).group_by(
        subq_absorp.c.uwi,
        subq_absorp.c.cid_all,
    ).subquery()

    stmt_profile = select(
        WellProfile.field,
        WellProfile.well_name,
        WellProfile.well_type,
        WellProfile.cid_all,
        WellProfile.rec_date,
        WellProfile.layer,
        WellProfile.diff_absorp,
        WellProfile.remarks,
    ).where(
        WellProfile.uwi == subq_rec_date.c.uwi,
        WellProfile.rec_date == subq_rec_date.c.max_date,
    ).subquery()

    subq_dat_rep = select(
        MonthlyReport.field,
        MonthlyReport.well_name,
        MonthlyReport.cid_all,
        func.max(MonthlyReport.dat_rep).label('max_date'),
    ).where(
        MonthlyReport.dat_rep >= update.date_from,
        MonthlyReport.dat_rep <= update.date_to,
        or_(
            MonthlyReport.water > 0,
            MonthlyReport.liquid > 0,
        ),
    ).group_by(
        MonthlyReport.field,
        MonthlyReport.well_name,
        MonthlyReport.cid_all,
    ).subquery()

    stmt = select(
        MonthlyReport.field,
        MonthlyReport.well_name,
        MonthlyReport.cid_all,
        MonthlyReport.cid,
        MonthlyReport.dat_rep,
        MonthlyReport.liq_rate,
        MonthlyReport.inj_rate,
        stmt_profile.c.well_type,
        stmt_profile.c.rec_date,
        stmt_profile.c.layer,
        stmt_profile.c.diff_absorp,
        stmt_profile.c.remarks,
    ).where(
        MonthlyReport.field == subq_dat_rep.c.field,
        MonthlyReport.well_name == subq_dat_rep.c.well_name,
        MonthlyReport.cid_all == subq_dat_rep.c.cid_all,
        MonthlyReport.dat_rep == subq_dat_rep.c.max_date,
    ).outerjoin(
        stmt_profile,
        and_(
            stmt_profile.c.field == MonthlyReport.field,
            stmt_profile.c.well_name == MonthlyReport.well_name,
            stmt_profile.c.cid_all == MonthlyReport.cid_all,
        ),
    )

    result = await session.execute(stmt)
    df = pd.DataFrame(result.all())
    df.to_csv('profiles.csv', encoding='cp1251', sep=';', index=False)

    return {'message': 'OK'}
