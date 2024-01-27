from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex import initializers, loaders
from app.infrastructure.db.dao.sql import ofm, reporters
from app.infrastructure.files.dao import csv, excel


class HolderDAO:
    def __init__(
        self,
        *,
        local_pool: async_sessionmaker[AsyncSession] | None = None,
        local_session: AsyncSession | None = None,
        ofm_pool: sessionmaker[Session] | None = None,
        ofm_session: Session | None = None,
        file_path: Path | None = None,
    ) -> None:
        self.local_pool = local_pool
        self.local_session = local_session
        self.ofm_pool = ofm_pool
        self.ofm_session = ofm_session
        self.file_path = file_path

    @property
    def local_monthly_report(self) -> local.MonthlyReportDAO:
        return local.MonthlyReportDAO(self.local_session)

    @property
    def local_well_profile(self) -> local.WellProfileDAO:
        return local.WellProfileDAO(self.local_session)

    @property
    def local_new_strategy_inj(self) -> local.NewStrategyInjDAO:
        return local.NewStrategyInjDAO(self.local_session)

    @property
    def local_field_replace(self) -> local.FieldReplaceDAO:
        return local.FieldReplaceDAO(self.local_session)

    @property
    def local_reservoir_replace(self) -> local.ReservoirReplaceDAO:
        return local.ReservoirReplaceDAO(self.local_session)

    @property
    def local_layer_replace(self) -> local.LayerReplaceDAO:
        return local.LayerReplaceDAO(self.local_session)

    @property
    def local_inj_well_database(self) -> local.InjWellDatabaseDAO:
        return local.InjWellDatabaseDAO(self.local_session)

    @property
    def local_new_strategy_oil(self) -> local.NewStrategyOilDAO:
        return local.NewStrategyOilDAO(self.local_session)

    @property
    def local_neighborhood(self) -> local.NeighborhoodDAO:
        return local.NeighborhoodDAO(self.local_session)

    @property
    def ofm_monthly_report(self) -> ofm.MonthlyReportDAO:
        return ofm.MonthlyReportDAO(self.ofm_session)

    @property
    def ofm_well_profile(self) -> ofm.WellProfileDAO:
        return ofm.WellProfileDAO(self.ofm_session)

    @property
    def ofm_field_list(self) -> ofm.FieldListDAO:
        return ofm.FieldListDAO(self.ofm_session)

    @property
    def ofm_reservoir_list(self) -> ofm.ReservoirListDAO:
        return ofm.ReservoirListDAO(self.ofm_session)

    @property
    def csv_monthly_report(self) -> csv.MonthlyReportDAO:
        return csv.MonthlyReportDAO(self.file_path)

    @property
    def csv_well_profile(self) -> csv.WellProfileDAO:
        return csv.WellProfileDAO(self.file_path)

    @property
    def csv_field_replace(self) -> csv.FieldReplaceDAO:
        return csv.FieldReplaceDAO(self.file_path)

    @property
    def csv_reservoir_replace(self) -> csv.ReservoirReplaceDAO:
        return csv.ReservoirReplaceDAO(self.file_path)

    @property
    def csv_layer_replace(self) -> csv.LayerReplaceDAO:
        return csv.LayerReplaceDAO(self.file_path)

    @property
    def csv_inj_well_database(self) -> csv.InjWellDatabaseDAO:
        return csv.InjWellDatabaseDAO(self.file_path)

    @property
    def csv_neighborhood(self) -> csv.NeighborhoodDAO:
        return csv.NeighborhoodDAO(self.file_path)

    @property
    def csv_new_strategy_inj(self) -> csv.NewStrategyInjDAO:
        return csv.NewStrategyInjDAO(self.file_path)

    @property
    def csv_new_strategy_oil(self) -> csv.NewStrategyOilDAO:
        return csv.NewStrategyOilDAO(self.file_path)

    @property
    def excel_new_strategy_inj(self) -> excel.NewStrategyInjDAO:
        return excel.NewStrategyInjDAO(self.file_path)

    @property
    def excel_new_strategy_oil(self) -> excel.NewStrategyOilDAO:
        return excel.NewStrategyOilDAO(self.file_path)

    @property
    def excel_inj_well_database(self) -> excel.InjWellDatabaseDAO:
        return excel.InjWellDatabaseDAO(self.file_path)

    @property
    def excel_neighborhood(self) -> excel.NeighborhoodDAO:
        return excel.NeighborhoodDAO(self.file_path)

    @property
    def monthly_report_initializer(
        self,
    ) -> initializers.MonthlyReportInitializer:
        return initializers.MonthlyReportInitializer(
            self.csv_monthly_report, self.local_monthly_report
        )

    @property
    def well_profile_initializer(self) -> initializers.WellProfileInitializer:
        return initializers.WellProfileInitializer(
            self.csv_well_profile, self.local_well_profile
        )

    @property
    def field_replace_initializer(
        self,
    ) -> initializers.FieldReplaceInitializer:
        return initializers.FieldReplaceInitializer(
            self.csv_field_replace, self.local_field_replace
        )

    @property
    def reservoir_replace_initializer(
        self,
    ) -> initializers.ReservoirReplaceInitializer:
        return initializers.ReservoirReplaceInitializer(
            self.csv_reservoir_replace, self.local_reservoir_replace
        )

    @property
    def layer_replace_initializer(
        self,
    ) -> initializers.LayerReplaceInitializer:
        return initializers.LayerReplaceInitializer(
            self.csv_layer_replace, self.local_layer_replace
        )

    @property
    def inj_well_database_initializer(
        self,
    ) -> initializers.InjWellDatabaseInitializer:
        return initializers.InjWellDatabaseInitializer(
            self.csv_inj_well_database, self.local_inj_well_database
        )

    @property
    def neighborhood_initializer(
        self,
    ) -> initializers.NeighborhoodInitializer:
        return initializers.NeighborhoodInitializer(
            self.csv_neighborhood, self.local_neighborhood
        )

    @property
    def new_strategy_inj_initializer(
        self,
    ) -> initializers.NewStrategyInjInitializer:
        return initializers.NewStrategyInjInitializer(
            self.csv_new_strategy_inj, self.local_new_strategy_inj
        )

    @property
    def new_strategy_oil_initializer(
        self,
    ) -> initializers.NewStrategyOilInitializer:
        return initializers.NewStrategyOilInitializer(
            self.csv_new_strategy_oil, self.local_new_strategy_oil
        )

    @property
    def well_profile_reporter(self) -> reporters.WellProfileReporter:
        return reporters.WellProfileReporter(self.local_pool)

    @property
    def first_rate_loss_reporter(self) -> reporters.FirstRateLossReporter:
        return reporters.FirstRateLossReporter(self.local_pool)

    @property
    def max_rate_loss_reporter(self) -> reporters.MaxRateLossReporter:
        return reporters.MaxRateLossReporter(self.local_pool)

    @property
    def opp_per_year_reporter(self) -> reporters.OppPerYearReporter:
        return reporters.OppPerYearReporter(self.ofm_pool)

    @property
    def new_strategy_inj_loader(self) -> loaders.NewStrategyInjLoader:
        return loaders.NewStrategyInjLoader(
            self.excel_new_strategy_inj, self.local_new_strategy_inj
        )

    @property
    def new_strategy_oil_loader(self) -> loaders.NewStrategyOilLoader:
        return loaders.NewStrategyOilLoader(
            self.excel_new_strategy_oil, self.local_new_strategy_oil
        )

    @property
    def inj_well_database_loader(self) -> loaders.InjWellDatabaseLoader:
        return loaders.InjWellDatabaseLoader(
            self.excel_inj_well_database, self.local_inj_well_database
        )

    @property
    def neighborhood_loader(self) -> loaders.NeighborhoodLoader:
        return loaders.NeighborhoodLoader(
            self.excel_neighborhood, self.local_neighborhood
        )

    @property
    def monthly_report_loader(self) -> loaders.MonthlyReportLoader:
        return loaders.MonthlyReportLoader(
            self.ofm_monthly_report, self.local_monthly_report
        )

    @property
    def well_profile_loader(self) -> loaders.WellProfileLoader:
        return loaders.WellProfileLoader(
            self.ofm_well_profile, self.local_well_profile
        )

    async def commit(self) -> None:
        await self.local_session.commit()
