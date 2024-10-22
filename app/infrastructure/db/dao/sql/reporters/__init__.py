from .base import BaseDAO
from .compensation import CompensationReporter
from .fnv import FnvReporter
from .inj_loss import FirstRateInjLossReporter, MaxRateInjLossReporter
from .local import LocalBaseDAO
from .matbal import MatbalReporter
from .matrix import MatrixReporter
from .mmb import MmbAltReporter, MmbReporter
from .ofm import OfmBaseDAO
from .oil_loss import FirstRateOilLossReporter, MaxRateOilLossReporter
from .opp_per_year import OppPerYearReporter
from .well_profile import WellProfileReporter
from .well_test import WellTestReporter
