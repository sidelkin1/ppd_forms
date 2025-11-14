from pydantic import BaseModel

from app.core.models.dto import UneftFieldDB, UneftReservoirDB


class MatbalParams(BaseModel):
    field: UneftFieldDB
    reservoirs: list[UneftReservoirDB]
    wells: str | None = None
    measurements: str | None = None
    alternative: bool
    stoiip: float = 10000
    wat_fvf: float = 1
    oil_fvf: float = 1.05
    init_pressure: float = 120
    init_swat: float = 0.25
    wat_compress: float = 4e-5
    rock_compress: float = 5e-5
    oil_compress: float = 8e-5
    near_transmiss: float = 1000
    far_transmiss: float = 10
    aquifer_volume: float = 100000
    injection_factor: float = 1
    thickness: float = 10
    wat_viscosity: float = 1.32
