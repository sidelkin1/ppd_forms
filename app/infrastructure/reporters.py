"""Reporters: предсобранные pool-based репортёры.

Локальные репортёры собираются всегда; OFM-репортёры — только если Oracle
сконфигурирован (иначе `None`, а их обработчики явно сообщают об ошибке).
"""

from dataclasses import dataclass

from app.infrastructure.db.dao.sql.reporters import (
    CompensationReporter,
    FirstRateInjLossReporter,
    FirstRateOilLossReporter,
    FnvReporter,
    LocalWellTestReporter,
    MatbalReporter,
    MatrixReporter,
    MaxRateInjLossReporter,
    MaxRateOilLossReporter,
    MmbAltReporter,
    MmbReporter,
    OfmWellTestReporter,
    OppPerYearReporter,
    OwcRespReporter,
    WellProfileReporter,
)
from app.infrastructure.sessions import Sessions


@dataclass(frozen=True)
class Reporters:
    profile: WellProfileReporter
    first_rate_inj_loss: FirstRateInjLossReporter
    max_rate_inj_loss: MaxRateInjLossReporter
    first_rate_oil_loss: FirstRateOilLossReporter
    max_rate_oil_loss: MaxRateOilLossReporter
    matrix: MatrixReporter
    well_test_local: LocalWellTestReporter
    opp_per_year: OppPerYearReporter | None
    fnv: FnvReporter | None
    matbal: MatbalReporter | None
    mmb: MmbReporter | None
    mmb_alt: MmbAltReporter | None
    owc_resp: OwcRespReporter | None
    compensation: CompensationReporter | None
    well_test_ofm: OfmWellTestReporter | None


def build_reporters(sessions: Sessions) -> Reporters:
    """Собирает репортёры один раз на старте (pool не меняется)."""
    local = sessions.local
    ofm = sessions.ofm
    return Reporters(
        profile=WellProfileReporter(local),
        first_rate_inj_loss=FirstRateInjLossReporter(local),
        max_rate_inj_loss=MaxRateInjLossReporter(local),
        first_rate_oil_loss=FirstRateOilLossReporter(local),
        max_rate_oil_loss=MaxRateOilLossReporter(local),
        matrix=MatrixReporter(local),
        well_test_local=LocalWellTestReporter(local),
        opp_per_year=OppPerYearReporter(ofm) if ofm else None,
        fnv=FnvReporter(ofm) if ofm else None,
        matbal=MatbalReporter(ofm) if ofm else None,
        mmb=MmbReporter(ofm) if ofm else None,
        mmb_alt=MmbAltReporter(ofm) if ofm else None,
        owc_resp=OwcRespReporter(ofm) if ofm else None,
        compensation=CompensationReporter(ofm) if ofm else None,
        well_test_ofm=OfmWellTestReporter(ofm) if ofm else None,
    )
