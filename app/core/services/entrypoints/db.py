from app.common.config.models.paths import Paths
from app.core.services import init_db
from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex import initializers
from app.infrastructure.files.dao import csv
from app.infrastructure.sessions import Sessions


async def init_field_replace(sessions: Sessions, paths: Paths) -> None:
    async with sessions.local_session() as session:
        await init_db.init_field_replace(
            initializers.FieldReplaceInitializer(
                csv.FieldReplaceDAO(paths.field_replace),
                local.FieldReplaceDAO(session),
            )
        )


async def init_reservoir_replace(sessions: Sessions, paths: Paths) -> None:
    async with sessions.local_session() as session:
        await init_db.init_reservoir_replace(
            initializers.ReservoirReplaceInitializer(
                csv.ReservoirReplaceDAO(paths.reservoir_replace),
                local.ReservoirReplaceDAO(session),
            )
        )


async def init_layer_replace(sessions: Sessions, paths: Paths) -> None:
    async with sessions.local_session() as session:
        await init_db.init_layer_replace(
            initializers.LayerReplaceInitializer(
                csv.LayerReplaceDAO(paths.layer_replace),
                local.LayerReplaceDAO(session),
            )
        )


async def init_gtm_replace(sessions: Sessions, paths: Paths) -> None:
    async with sessions.local_session() as session:
        await init_db.init_gtm_replace(
            initializers.GtmReplaceInitializer(
                csv.GtmReplaceDAO(paths.gtm_replace),
                local.GtmReplaceDAO(session),
            )
        )


async def init_monthly_report(sessions: Sessions, paths: Paths) -> None:
    async with sessions.local_session() as session:
        await init_db.init_monthly_report(
            initializers.MonthlyReportInitializer(
                csv.MonthlyReportDAO(paths.monthly_report),
                local.MonthlyReportDAO(session),
            )
        )


async def init_well_profile(sessions: Sessions, paths: Paths) -> None:
    async with sessions.local_session() as session:
        await init_db.init_well_profile(
            initializers.WellProfileInitializer(
                csv.WellProfileDAO(paths.well_profile),
                local.WellProfileDAO(session),
            )
        )


async def init_inj_well_database(sessions: Sessions, paths: Paths) -> None:
    async with sessions.local_session() as session:
        await init_db.init_inj_well_database(
            initializers.InjWellDatabaseInitializer(
                csv.InjWellDatabaseDAO(paths.inj_well_database),
                local.InjWellDatabaseDAO(session),
            )
        )


async def init_neighborhood(sessions: Sessions, paths: Paths) -> None:
    async with sessions.local_session() as session:
        await init_db.init_neighborhood(
            initializers.NeighborhoodInitializer(
                csv.NeighborhoodDAO(paths.neighborhood),
                local.NeighborhoodDAO(session),
            )
        )


async def init_new_strategy_inj(sessions: Sessions, paths: Paths) -> None:
    async with sessions.local_session() as session:
        await init_db.init_new_strategy_inj(
            initializers.NewStrategyInjInitializer(
                csv.NewStrategyInjDAO(paths.new_strategy_inj),
                local.NewStrategyInjDAO(session),
            )
        )


async def init_new_strategy_oil(sessions: Sessions, paths: Paths) -> None:
    async with sessions.local_session() as session:
        await init_db.init_new_strategy_oil(
            initializers.NewStrategyOilInitializer(
                csv.NewStrategyOilDAO(paths.new_strategy_oil),
                local.NewStrategyOilDAO(session),
            )
        )


async def init_well_test(sessions: Sessions, paths: Paths) -> None:
    async with sessions.local_session() as session:
        await init_db.init_well_test(
            initializers.WellTestInitializer(
                csv.WellTestDAO(paths.well_test),
                local.WellTestDAO(session),
            )
        )
