import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("url", ["/", "/reports", "/tables"])
@pytest.mark.asyncio(scope="session")
async def test_home(client: AsyncClient, url: str):
    resp = await client.get(url, follow_redirects=True)
    assert resp.is_success
