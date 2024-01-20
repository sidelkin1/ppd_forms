import pytest

from app.infrastructure.db.dao.complex.loaders import BaseLoader
from app.infrastructure.db.dao.local import MainTableDAO
from app.infrastructure.holder import HolderDAO


@pytest.mark.parametrize(
    "dao,loader,init_count",
    [
        ("local_new_strategy_inj", "new_strategy_inj_loader", 2),
        ("local_new_strategy_oil", "new_strategy_oil_loader", 3),
        ("local_inj_well_database", "inj_well_database_loader", 2),
        ("local_neighborhood", "neighborhood_loader", 4),
        ("local_well_profile", "well_profile_loader", 6),
        ("local_monthly_report", "monthly_report_loader", 23),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_loads(
    holder: HolderDAO, dao: str, loader: str, init_count: int
):
    try:
        dao_: MainTableDAO = getattr(holder, dao)
        loader_: BaseLoader = getattr(holder, loader)
        objs = await dao_.get_all()
        count = await dao_.count()
        assert count == init_count
        await loader_.refresh()
        count = await dao_.count()
        assert count == init_count + 1
        await loader_.reload()
        count = await dao_.count()
        assert count == 1
        await dao_.reload(objs)
        await dao_.commit()
        count = await dao_.count()
        assert count == init_count
    except NotImplementedError:
        pytest.skip("Not implemented")
