from enum import Enum


class ReportName(str, Enum):
    profile = "profile"
    inj_loss = "inj_loss"
    oil_loss = "oil_loss"
    opp_per_year = "opp_per_year"
    matrix = "matrix"
    fnv = "fnv"
    matbal = "matbal"
    prolong = "prolong"
    mmb = "mmb"
    compensation = "compensation"
