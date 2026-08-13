from datetime import date

from app.core.models.dto.db.field_list import UneftFieldDB
from app.core.models.dto.db.reservoir_list import UneftReservoirDB
from app.core.models.dto.tasks.report import TaskReport
from app.core.models.enums import TaskId, WellTest


class TaskOwcResp(
    TaskReport, task_id=TaskId.report, route_fields=["task_id", "name"]
):
    field: UneftFieldDB
    reservoir: UneftReservoirDB
    well: str
    pressure: float
    depth: float
    well_test: WellTest
    on_date: date

    @property
    def filename_prefix(self) -> str:
        return f"{self.field.name}_{self.reservoir.name}_{self.well}"
