from pydantic import NonNegativeFloat
from pydantic_settings import BaseSettings


class Parameter(BaseSettings):
    name: str
    min_value: NonNegativeFloat
    max_value: NonNegativeFloat
    symbols: list[str]


class PressureTolerance(BaseSettings):
    min_value: NonNegativeFloat
    max_value: NonNegativeFloat


class MmbSettings(BaseSettings):
    params: list[Parameter]
    press_tol: PressureTolerance
