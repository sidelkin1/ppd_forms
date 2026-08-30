from typing import Any

import pytest

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex import loaders
from tests.mocks.excel_dao import (
    InjWellDatabaseMock,
    NeighborhoodMock,
    NewStrategyInjMock,
    NewStrategyOilMock,
)
from tests.mocks.ofm_dao import MonthlyReportMock, WellProfileMock


def _make(
    name: str, session: Any
) -> tuple[local.MainTableDAO[Any, Any], loaders.BaseLoader[Any, Any]]:
    dao: local.MainTableDAO[Any, Any]
    if name == "new_strategy_inj":
        dao = local.NewStrategyInjDAO(session)
        return dao, loaders.NewStrategyInjLoader(
            NewStrategyInjMock(None, ","), dao
        )
    if name == "new_strategy_oil":
        dao = local.NewStrategyOilDAO(session)
        return dao, loaders.NewStrategyOilLoader(NewStrategyOilMock(None), dao)
    if name == "inj_well_database":
        dao = local.InjWellDatabaseDAO(session)
        return dao, loaders.InjWellDatabaseLoader(
            InjWellDatabaseMock(None), dao
        )
    if name == "neighborhood":
        dao = local.NeighborhoodDAO(session)
        return dao, loaders.NeighborhoodLoader(NeighborhoodMock(None), dao)
    if name == "well_profile":
        dao = local.WellProfileDAO(session)
        return dao, loaders.WellProfileLoader(WellProfileMock(None), dao)
    if name == "monthly_report":
        dao = local.MonthlyReportDAO(session)
        return dao, loaders.MonthlyReportLoader(MonthlyReportMock(None), dao)
    raise ValueError(name)


@pytest.mark.parametrize(
    "name,init_count",
    [
        ("new_strategy_inj", 2),
        ("new_strategy_oil", 3),
        ("inj_well_database", 2),
        ("neighborhood", 4),
        ("well_profile", 6),
        ("monthly_report", 23),
    ],
)
@pytest.mark.asyncio
async def test_loads(session, name: str, init_count: int):
    try:
        dao, loader = _make(name, session)
        objs = await dao.get_all()
        count = await dao.count()
        assert count == init_count
        await loader.refresh()
        count = await dao.count()
        assert count == init_count + 1
        await loader.reload()
        count = await dao.count()
        assert count == 1
        await dao.reload(objs)
        await dao.commit()
        count = await dao.count()
        assert count == init_count
    except NotImplementedError:
        pytest.skip("Not implemented")
