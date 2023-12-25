from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex import initializer, loader
from app.infrastructure.db.dao.query import ofm, reporter
from app.infrastructure.files.dao import csv, excel


class HolderDAO:
    def __init__(
        self,
        *,
        local_pool: async_sessionmaker[AsyncSession] | None = None,
        local_session: AsyncSession | None = None,
        ofm_session: Session | None = None,
        excel_path: Path | None = None,
    ) -> None:
        self.local_pool = local_pool
        self.local_session = local_session
        self.ofm_session = ofm_session
        self.excel_path = excel_path

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
    def csv_monthly_report(self) -> csv.MonthlyReportDAO:
        return csv.MonthlyReportDAO(settings.monthly_report_path)

    @property
    def csv_well_profile(self) -> csv.WellProfileDAO:
        return csv.WellProfileDAO(settings.well_profile_path)

    @property
    def csv_field_replace(self) -> csv.FieldReplaceDAO:
        return csv.FieldReplaceDAO(settings.field_replace_path)

    @property
    def csv_reservoir_replace(self) -> csv.ReservoirReplaceDAO:
        return csv.ReservoirReplaceDAO(settings.reservoir_replace_path)

    @property
    def csv_layer_replace(self) -> csv.LayerReplaceDAO:
        return csv.LayerReplaceDAO(settings.layer_replace_path)

    @property
    def excel_new_strategy_inj(self) -> excel.NewStrategyInjDAO:
        return excel.NewStrategyInjDAO(self.excel_path)

    @property
    def excel_new_strategy_oil(self) -> excel.NewStrategyOilDAO:
        return excel.NewStrategyOilDAO(self.excel_path)

    @property
    def excel_inj_well_database(self) -> excel.InjWellDatabaseDAO:
        return excel.InjWellDatabaseDAO(self.excel_path)

    @property
    def excel_neighborhood(self) -> excel.NeighborhoodDAO:
        return excel.NeighborhoodDAO(self.excel_path)

    @property
    def monthly_report_initializer(
        self,
    ) -> initializer.MonthlyReportInitializer:
        return initializer.MonthlyReportInitializer(
            self.csv_monthly_report, self.local_monthly_report
        )

    @property
    def well_profile_initializer(self) -> initializer.WellProfileInitializer:
        return initializer.WellProfileInitializer(
            self.csv_well_profile, self.local_well_profile
        )

    @property
    def field_replace_initializer(self) -> initializer.FieldReplaceInitializer:
        return initializer.FieldReplaceInitializer(
            self.csv_field_replace, self.local_field_replace
        )

    @property
    def reservoir_replace_initializer(
        self,
    ) -> initializer.ReservoirReplaceInitializer:
        return initializer.ReservoirReplaceInitializer(
            self.csv_reservoir_replace, self.local_reservoir_replace
        )

    @property
    def layer_replace_initializer(self) -> initializer.LayerReplaceInitializer:
        return initializer.LayerReplaceInitializer(
            self.csv_layer_replace, self.local_layer_replace
        )

    @property
    def well_profile_reporter(self) -> reporter.WellProfileReporter:
        return reporter.WellProfileReporter(self.local_pool)

    @property
    def first_rate_loss_reporter(self) -> reporter.FirstRateLossReporter:
        return reporter.FirstRateLossReporter(self.local_pool)

    @property
    def max_rate_loss_reporter(self) -> reporter.MaxRateLossReporter:
        return reporter.MaxRateLossReporter(self.local_pool)

    @property
    def new_strategy_inj_loader(self) -> loader.NewStrategyInjLoader:
        return loader.NewStrategyInjLoader(
            self.excel_new_strategy_inj, self.local_new_strategy_inj
        )

    @property
    def new_strategy_oil_loader(self) -> loader.NewStrategyOilLoader:
        return loader.NewStrategyOilLoader(
            self.excel_new_strategy_oil, self.local_new_strategy_oil
        )

    @property
    def inj_well_database_loader(self) -> loader.InjWellDatabaseLoader:
        return loader.InjWellDatabaseLoader(
            self.excel_inj_well_database, self.local_inj_well_database
        )

    @property
    def neighborhood_loader(self) -> loader.NeighborhoodLoader:
        return loader.NeighborhoodLoader(
            self.excel_neighborhood, self.local_neighborhood
        )

    @property
    def monthly_report_loader(self) -> loader.MonthlyReportLoader:
        return loader.MonthlyReportLoader(
            self.ofm_monthly_report, self.local_monthly_report
        )

    @property
    def well_profile_loader(self) -> loader.WellProfileLoader:
        return loader.WellProfileLoader(
            self.ofm_well_profile, self.local_well_profile
        )

    async def commit(self) -> None:
        await self.local_session.commit()
