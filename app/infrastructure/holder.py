from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex import initializers, loaders, uneft
from app.infrastructure.db.dao.complex import reporters as complex_reporters
from app.infrastructure.db.dao.sql import ofm
from app.infrastructure.db.dao.sql import reporters as db_reporters
from app.infrastructure.files.dao import csv, excel
from app.infrastructure.files.dao import reporters as file_reporters


class HolderDAO:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    @property
    def local_monthly_report(self) -> local.MonthlyReportDAO:
        return local.MonthlyReportDAO(self.kwargs["local_session"])

    @property
    def local_well_profile(self) -> local.WellProfileDAO:
        return local.WellProfileDAO(self.kwargs["local_session"])

    @property
    def local_new_strategy_inj(self) -> local.NewStrategyInjDAO:
        return local.NewStrategyInjDAO(self.kwargs["local_session"])

    @property
    def local_field_replace(self) -> local.FieldReplaceDAO:
        return local.FieldReplaceDAO(self.kwargs["local_session"])

    @property
    def local_reservoir_replace(self) -> local.ReservoirReplaceDAO:
        return local.ReservoirReplaceDAO(self.kwargs["local_session"])

    @property
    def local_layer_replace(self) -> local.LayerReplaceDAO:
        return local.LayerReplaceDAO(self.kwargs["local_session"])

    @property
    def local_gtm_replace(self) -> local.GtmReplaceDAO:
        return local.GtmReplaceDAO(self.kwargs["local_session"])

    @property
    def local_inj_well_database(self) -> local.InjWellDatabaseDAO:
        return local.InjWellDatabaseDAO(self.kwargs["local_session"])

    @property
    def local_new_strategy_oil(self) -> local.NewStrategyOilDAO:
        return local.NewStrategyOilDAO(self.kwargs["local_session"])

    @property
    def local_neighborhood(self) -> local.NeighborhoodDAO:
        return local.NeighborhoodDAO(self.kwargs["local_session"])

    @property
    def local_well_test(self) -> local.WellTestDAO:
        return local.WellTestDAO(self.kwargs["local_session"])

    @property
    def ofm_monthly_report(self) -> ofm.MonthlyReportDAO:
        return ofm.MonthlyReportDAO(self.kwargs["ofm_session"])

    @property
    def ofm_well_profile(self) -> ofm.WellProfileDAO:
        return ofm.WellProfileDAO(self.kwargs["ofm_session"])

    @property
    def ofm_field_list(self) -> ofm.FieldListDAO:
        return ofm.FieldListDAO(
            self.kwargs["ofm_session"],
            self.kwargs["redis"],
            self.kwargs["expires"],
        )

    @property
    def ofm_reservoir_list(self) -> ofm.ReservoirListDAO:
        return ofm.ReservoirListDAO(
            self.kwargs["ofm_session"],
            self.kwargs["redis"],
            self.kwargs["expires"],
        )

    @property
    def ofm_well_list(self) -> ofm.WellListDAO:
        return ofm.WellListDAO(
            self.kwargs["ofm_session"],
            self.kwargs["redis"],
            self.kwargs["expires"],
        )

    @property
    def csv_monthly_report(self) -> csv.MonthlyReportDAO:
        return csv.MonthlyReportDAO(self.kwargs["file_path"])

    @property
    def csv_well_profile(self) -> csv.WellProfileDAO:
        return csv.WellProfileDAO(self.kwargs["file_path"])

    @property
    def csv_field_replace(self) -> csv.FieldReplaceDAO:
        return csv.FieldReplaceDAO(self.kwargs["file_path"])

    @property
    def csv_reservoir_replace(self) -> csv.ReservoirReplaceDAO:
        return csv.ReservoirReplaceDAO(self.kwargs["file_path"])

    @property
    def csv_layer_replace(self) -> csv.LayerReplaceDAO:
        return csv.LayerReplaceDAO(self.kwargs["file_path"])

    @property
    def csv_gtm_replace(self) -> csv.GtmReplaceDAO:
        return csv.GtmReplaceDAO(self.kwargs["file_path"])

    @property
    def csv_inj_well_database(self) -> csv.InjWellDatabaseDAO:
        return csv.InjWellDatabaseDAO(self.kwargs["file_path"])

    @property
    def csv_neighborhood(self) -> csv.NeighborhoodDAO:
        return csv.NeighborhoodDAO(self.kwargs["file_path"])

    @property
    def csv_new_strategy_inj(self) -> csv.NewStrategyInjDAO:
        return csv.NewStrategyInjDAO(self.kwargs["file_path"])

    @property
    def csv_new_strategy_oil(self) -> csv.NewStrategyOilDAO:
        return csv.NewStrategyOilDAO(self.kwargs["file_path"])

    @property
    def csv_well_test(self) -> csv.WellTestDAO:
        return csv.WellTestDAO(self.kwargs["file_path"])

    @property
    def excel_new_strategy_inj(self) -> excel.NewStrategyInjDAO:
        return excel.NewStrategyInjDAO(
            self.kwargs["file_path"], self.kwargs["delimiter"]
        )

    @property
    def excel_new_strategy_oil(self) -> excel.NewStrategyOilDAO:
        return excel.NewStrategyOilDAO(self.kwargs["file_path"])

    @property
    def excel_inj_well_database(self) -> excel.InjWellDatabaseDAO:
        return excel.InjWellDatabaseDAO(self.kwargs["file_path"])

    @property
    def excel_neighborhood(self) -> excel.NeighborhoodDAO:
        return excel.NeighborhoodDAO(self.kwargs["file_path"])

    @property
    def excel_prolong_expected(self) -> excel.ProlongExpectedDAO:
        return excel.ProlongExpectedDAO(self.kwargs["file_path"])

    @property
    def excel_well_test(self) -> excel.WellTestDAO:
        return excel.WellTestDAO(self.kwargs["file_path"])

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
    def gtm_replace_initializer(
        self,
    ) -> initializers.GtmReplaceInitializer:
        return initializers.GtmReplaceInitializer(
            self.csv_gtm_replace, self.local_gtm_replace
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
    def well_test_initializer(self) -> initializers.WellTestInitializer:
        return initializers.WellTestInitializer(
            self.csv_well_test, self.local_well_test
        )

    @property
    def well_profile_reporter(self) -> db_reporters.WellProfileReporter:
        return db_reporters.WellProfileReporter(self.kwargs["local_pool"])

    @property
    def first_rate_inj_loss_reporter(
        self,
    ) -> db_reporters.FirstRateInjLossReporter:
        return db_reporters.FirstRateInjLossReporter(self.kwargs["local_pool"])

    @property
    def max_rate_inj_loss_reporter(
        self,
    ) -> db_reporters.MaxRateInjLossReporter:
        return db_reporters.MaxRateInjLossReporter(self.kwargs["local_pool"])

    @property
    def first_rate_oil_loss_reporter(
        self,
    ) -> db_reporters.FirstRateOilLossReporter:
        return db_reporters.FirstRateOilLossReporter(self.kwargs["local_pool"])

    @property
    def max_rate_oil_loss_reporter(
        self,
    ) -> db_reporters.MaxRateOilLossReporter:
        return db_reporters.MaxRateOilLossReporter(self.kwargs["local_pool"])

    @property
    def opp_per_year_reporter(self) -> db_reporters.OppPerYearReporter:
        return db_reporters.OppPerYearReporter(self.kwargs["ofm_pool"])

    @property
    def db_matrix_reporter(self) -> db_reporters.MatrixReporter:
        return db_reporters.MatrixReporter(self.kwargs["local_pool"])

    @property
    def fnv_reporter(self) -> db_reporters.FnvReporter:
        return db_reporters.FnvReporter(self.kwargs["ofm_pool"])

    @property
    def db_matbal_reporter(self) -> db_reporters.MatbalReporter:
        return db_reporters.MatbalReporter(self.kwargs["ofm_pool"])

    @property
    def db_mmb_reporter(self) -> db_reporters.MmbReporter:
        return db_reporters.MmbReporter(self.kwargs["ofm_pool"])

    @property
    def db_mmb_alt_reporter(self) -> db_reporters.MmbAltReporter:
        return db_reporters.MmbAltReporter(self.kwargs["ofm_pool"])

    @property
    def db_local_well_test_reporter(
        self,
    ) -> db_reporters.LocalWellTestReporter:
        return db_reporters.LocalWellTestReporter(self.kwargs["local_pool"])

    @property
    def db_ofm_well_test_reporter(self) -> db_reporters.OfmWellTestReporter:
        return db_reporters.OfmWellTestReporter(self.kwargs["ofm_pool"])

    @property
    def file_matbal_reporter(self) -> file_reporters.MatbalReporter:
        return file_reporters.MatbalReporter(
            self.kwargs["path"],
            self.kwargs["wells"],
            self.kwargs["measurements"],
        )

    @property
    def file_mmb_reporter(self) -> file_reporters.MmbReporter:
        return file_reporters.MmbReporter(self.kwargs["path"])

    @property
    def file_well_test_reporter(self) -> file_reporters.WellTestReporter:
        return file_reporters.WellTestReporter(
            self.kwargs["path"], self.kwargs["delimiter"]
        )

    @property
    def file_matrix_reporter(self) -> file_reporters.MatrixReporter:
        return file_reporters.MatrixReporter(
            self.kwargs["path"], self.kwargs["wells"]
        )

    @property
    def matbal_reporter(self) -> complex_reporters.MatbalReporter:
        return complex_reporters.MatbalReporter(
            self.db_matbal_reporter, self.file_matbal_reporter
        )

    @property
    def mmb_reporter(self) -> complex_reporters.MmbReporter:
        return complex_reporters.MmbReporter(
            self.db_mmb_reporter,
            self.db_mmb_alt_reporter,
            self.file_mmb_reporter,
        )

    @property
    def well_test_reporter(self) -> complex_reporters.WellTestReporter:
        return complex_reporters.WellTestReporter(
            self.db_local_well_test_reporter,
            self.file_well_test_reporter,
            self.db_ofm_well_test_reporter,
        )

    @property
    def compensation_reporter(self) -> db_reporters.CompensationReporter:
        return db_reporters.CompensationReporter(self.kwargs["ofm_pool"])

    @property
    def matrix_reporter(self) -> complex_reporters.MatrixReporter:
        return complex_reporters.MatrixReporter(
            self.db_matrix_reporter, self.file_matrix_reporter
        )

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

    @property
    def well_test_loader(self) -> loaders.WellTestLoader:
        return loaders.WellTestLoader(
            self.excel_well_test, self.local_well_test
        )

    @property
    def uneft(self) -> uneft.UneftDAO:
        return uneft.UneftDAO(
            self.ofm_field_list, self.ofm_reservoir_list, self.ofm_well_list
        )

    async def commit(self) -> None:
        await self.kwargs["local_session"].commit()
