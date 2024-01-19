import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "url",
    ["excel/ns_ppd", "excel/ns_oil", "database/report", "database/profile"],
)
@pytest.mark.asyncio(scope="session")
async def test_get_dates(client: AsyncClient, url: str):
    resp = await client.get(url)
    assert resp.is_success
    data = resp.json()
    assert data == {"min_date": "2000-01-01", "max_date": "2001-01-01"}


@pytest.mark.parametrize("url", ["excel/unknown", "database/unknown"])
@pytest.mark.asyncio(scope="session")
async def test_get_dates_unknown_table(client: AsyncClient, url: str):
    resp = await client.get(url)
    assert not resp.is_success
