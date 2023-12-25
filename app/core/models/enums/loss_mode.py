from enum import Enum


class LossMode(str, Enum):
    first_rate = "first_rate"
    max_rate = "max_rate"
