from enum import Enum


class ReportName(str, Enum):
    profile = "profile"
    oil_loss = "oil_loss"
    opp_per_year = "opp_per_year"
    matrix = "matrix"
