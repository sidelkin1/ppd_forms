from pydantic import BaseModel

from app.core.models.dto import UneftFieldDB, UneftReservoirDB


class MatbalParams(BaseModel):
    field: UneftFieldDB
    reservoirs: list[UneftReservoirDB]
    wells: str | None = None
    measurements: str | None = None
    alternative: bool
    stoiip: float | None = 10000
    wat_fvf: float | None = 1
    oil_fvf: float | None = 1.05
    init_pressure: float | None = 120
    init_swat: float | None = 0.25
    wat_compress: float | None = 4e-5
    rock_compress: float | None = 5e-5
    oil_compress: float | None = 8e-5
    near_transmiss: float | None = 1000
    far_transmiss: float | None = 10
    aquifer_volume: float | None = 100000
    injection_factor: float | None = 1
    thickness: float | None = 10
    wat_viscosity: float | None = 1.32
