from app.infrastructure.db.dao.sql import ofm, reporters
from app.infrastructure.files.dao import excel
from app.infrastructure.holder import HolderDAO
from tests.mocks.excel_dao import (
    InjWellDatabaseMock,
    NeighborhoodMock,
    NewStrategyInjMock,
    NewStrategyOilMock,
)
from tests.mocks.ofm_dao import MonthlyReportMock, WellProfileMock
from tests.mocks.reporters import FnvMock, OppPerYearMock
from tests.mocks.uneft import FieldListMock, ReservoirListMock, WellListMock


class HolderMock(HolderDAO):
    @property
    def ofm_monthly_report(self) -> ofm.MonthlyReportDAO:
        return MonthlyReportMock(self.kwargs["ofm_session"])

    @property
    def ofm_well_profile(self) -> ofm.WellProfileDAO:
        return WellProfileMock(self.kwargs["ofm_session"])

    @property
    def excel_new_strategy_inj(self) -> excel.NewStrategyInjDAO:
        return NewStrategyInjMock(self.kwargs["file_path"], ",")

    @property
    def excel_new_strategy_oil(self) -> excel.NewStrategyOilDAO:
        return NewStrategyOilMock(self.kwargs["file_path"])

    @property
    def excel_inj_well_database(self) -> excel.InjWellDatabaseDAO:
        return InjWellDatabaseMock(self.kwargs["file_path"])

    @property
    def excel_neighborhood(self) -> excel.NeighborhoodDAO:
        return NeighborhoodMock(self.kwargs["file_path"])

    @property
    def opp_per_year_reporter(self) -> reporters.OppPerYearReporter:
        return OppPerYearMock(self.kwargs["ofm_pool"])

    @property
    def fnv_reporter(self) -> reporters.FnvReporter:
        return FnvMock(self.kwargs["ofm_pool"])

    @property
    def ofm_field_list(self) -> ofm.FieldListDAO:
        return FieldListMock(self.kwargs["ofm_session"])

    @property
    def ofm_reservoir_list(self) -> ofm.ReservoirListDAO:
        return ReservoirListMock(self.kwargs["ofm_session"])

    @property
    def ofm_well_list(self) -> ofm.WellListDAO:
        return WellListMock(self.kwargs["ofm_session"])
