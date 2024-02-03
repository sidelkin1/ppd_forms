import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.config.settings import Settings


@pytest.mark.parametrize(
    "url",
    ["excel/ns_ppd", "excel/ns_oil", "database/report", "database/profile"],
)
@pytest.mark.asyncio(scope="session")
async def test_api_not_authorized(anon_client: AsyncClient, url: str):
    resp = await anon_client.get(url)
    assert not resp.is_success
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("url", ["/reports", "/tables"])
@pytest.mark.asyncio(scope="session")
async def test_home_not_authorized(anon_client: AsyncClient, url: str):
    resp = await anon_client.get(url)
    assert resp.is_redirect
    assert "/login" in resp.headers["Location"]


@pytest.mark.asyncio(scope="session")
async def test_login(anon_client: AsyncClient, settings: Settings):
    data = {
        "username": settings.app_default_username,
        "password": settings.app_default_password,
    }
    resp = await anon_client.post("/auth/token", data=data)
    assert resp.is_success
    token_data = resp.json()
    assert "access_token" in token_data
    assert "access_token" in resp.cookies
    assert (
        f"Bearer {token_data['access_token']}" in resp.cookies["access_token"]
    )


@pytest.mark.asyncio(scope="session")
async def test_logout(client: AsyncClient):
    resp = await client.post("/auth/revoke")
    assert resp.is_success
    assert "access_token" not in resp.cookies
    data = resp.json()
    assert {"message": "Выход из учетной записи!"} == data
