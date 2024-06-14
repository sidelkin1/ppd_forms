from enum import Enum


class Interpolation(str, Enum):
    akima = "akima"
    pchip = "pchip"
    cubic = "cubic"
