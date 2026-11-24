from datetime import date

from app.core.models.dto import TaskOwcResp, UneftFieldDB, UneftReservoirDB
from app.core.models.enums import ReportName, WellTest
from app.core.models.schemas import OwcRespParams

FIELD = UneftFieldDB(id=1, name="FIELD")
RESERVOIR = UneftReservoirDB(id=2, name="RESERVOIR")


def _params(**kwargs) -> OwcRespParams:
    payload = {
        "field": FIELD,
        "reservoir": RESERVOIR,
        "well": "  w1  ",
        "pressure": 100,
        "depth": 75,
        "well_test": WellTest.complex,
        "on_date": date(2025, 10, 20),
    }
    payload.update(kwargs)
    return OwcRespParams(**payload)


def test_params_accept_complex():
    params = _params()
    assert params.well_test is WellTest.complex
    assert params.well == "W1"


def test_params_serializes_complex():
    dump = _params().model_dump(mode="json")
    assert dump["well_test"] == "complex"
    assert set(dump) == {
        "field",
        "reservoir",
        "well",
        "pressure",
        "depth",
        "well_test",
        "on_date",
    }


def test_task_accepts_and_serializes_complex():
    task = TaskOwcResp(
        name=ReportName.owc_resp,
        field=FIELD,
        reservoir=RESERVOIR,
        well="W1",
        pressure=100,
        depth=75,
        well_test=WellTest.complex,
        on_date=date(2025, 10, 20),
    )
    assert task.well_test is WellTest.complex
    assert task.model_dump(mode="json")["well_test"] == "complex"
    assert TaskOwcResp.model_validate(task.model_dump()).well_test is (
        WellTest.complex
    )
