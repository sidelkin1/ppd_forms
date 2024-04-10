from enum import Enum


class ReportName(str, Enum):
    profile = "profile"
    inj_loss = "inj_loss"
    opp_per_year = "opp_per_year"
    matrix = "matrix"
