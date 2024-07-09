from .compensation import select_compensation_rates
from .matbal import (
    select_field_sum_alternative_rates,
    select_field_sum_rates,
    select_well_sum_alternative_rates,
    select_well_sum_rates,
)
from .mmb import (
    select_tank_alternative_rates,
    select_tank_bhp,
    select_tank_pressures,
    select_tank_rates,
    select_tank_works,
)
from .oil_loss import (
    select_monthly_report_for_first_rate,
    select_monthly_report_for_max_rate,
)
from .opp_per_year import select_well_profiles
from .well_profile import select_profile_report
