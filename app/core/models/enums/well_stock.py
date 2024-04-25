from enum import Enum


class WellStock(str, Enum):
    all = "all"
    production = "production"
    injection = "injection"
