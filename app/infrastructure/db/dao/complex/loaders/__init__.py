from .base import BaseLoader
from .excel_loader import ExcelLoader, ExcelLoaderFactory, excel_loader_factory
from .factory import LoaderFactory, loader_factory
from .inj_well_database import InjWellDatabaseLoader, inj_well_database_loader
from .monthly_report import MonthlyReportLoader, monthly_report_loader
from .neighborhood import NeighborhoodLoader, neighborhood_loader
from .new_strategy_inj import NewStrategyInjLoader, new_strategy_inj_loader
from .new_strategy_oil import NewStrategyOilLoader, new_strategy_oil_loader
from .ofm_loader import OfmLoader, OfmLoaderFactory, ofm_loader_factory
from .well_profile import WellProfileLoader, well_profile_loader
from .well_test import WellTestLoader, well_test_loader
