from app.core.models.dto import (
    InjWellDatabaseDB,
    NeighborhoodDB,
    NewStrategyInjDB,
    NewStrategyOilDB,
)
from app.infrastructure.files.dao.excel import (
    InjWellDatabaseDAO,
    NeighborhoodDAO,
    NewStrategyInjDAO,
    NewStrategyOilDAO,
)


class InjWellDatabaseMock(InjWellDatabaseDAO):
    async def get_all(self) -> list[InjWellDatabaseDB]:
        return [InjWellDatabaseDB(field="F2", well="W100")]


class NeighborhoodMock(NeighborhoodDAO):
    async def get_all(self) -> list[NeighborhoodDB]:
        return [
            NeighborhoodDB(
                field="F2", reservoir="R1", well="I100", neighbs="X1,X2"
            )
        ]


class NewStrategyInjMock(NewStrategyInjDAO):
    async def get_all(self) -> list[NewStrategyInjDB]:
        return [
            NewStrategyInjDB(
                field="F2",
                well="W100",
                reservoir="R1",
                gtm_description="GTM",
                gtm_date="2000-01-01",
                oil_recovery=None,
                effect_end=None,
                gtm_group="Group",
                oil_rate=None,
                gtm_problem="Problem",
                reservoir_neighbs=None,
                neighbs=None,
            )
        ]


class NewStrategyOilMock(NewStrategyOilDAO):
    async def get_all(self) -> list[NewStrategyOilDB]:
        return [
            NewStrategyOilDB(
                field="F2",
                well="W100",
                reservoir_before="R1",
                reservoir_after="R2",
                vnr_date="2000-01-01",
                gtm_name="GTM",
                start_date="2000-01-01",
            )
        ]
