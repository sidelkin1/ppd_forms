from dataclasses import dataclass, field
from datetime import date

from app.core.models.enums import LossMode
from app.infrastructure.db.dao.query.reporter import (
    FirstRateLossReporter,
    MaxRateLossReporter,
)


@dataclass
class OilLossReporter:
    first_rate: FirstRateLossReporter
    max_rate: MaxRateLossReporter
    _dao_mapper: dict[
        LossMode, FirstRateLossReporter | MaxRateLossReporter
    ] = field(init=False)

    def __post_init__(self):
        self._dao_mapper = {
            LossMode.first_rate: self.first_rate,
            LossMode.max_rate: self.max_rate,
        }

    def read_all(self, loss_mode: LossMode, date_from: date, date_to: date):
        return self._dao_mapper[loss_mode].read_all(
            date_from=date_from, date_to=date_to
        )
