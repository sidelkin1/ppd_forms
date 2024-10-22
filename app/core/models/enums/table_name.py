from enum import Enum


class OfmTableName(str, Enum):
    report = "report"
    profile = "profile"


class ExcelTableName(str, Enum):
    ns_ppd = "ns_ppd"
    ns_oil = "ns_oil"
    inj_db = "inj_db"
    neighbs = "neighbs"
    gdis = "gdis"
