from enum import Enum


class WellTest(str, Enum):
    static_level = "static_level"
    pressure = "pressure"
