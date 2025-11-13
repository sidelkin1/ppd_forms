import asyncio

import pytest
from fastapi import WebSocketDisconnect, status
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.api.config.models.auth import AuthSettings


@pytest.mark.parametrize(
    "url",
    [
        "/excel/ns_ppd",
        "/excel/ns_oil",
        "/database/report",
        "/database/profile",
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_api_not_authenticated(anon_client: AsyncClient, url: str):
    resp = await anon_client.get(url)
    assert not resp.is_success
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(scope="session")
async def test_websocket_not_authenticated(anon_test_client: TestClient):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with anon_test_client.websocket_connect("/jobs/111/ws"):
            await asyncio.sleep(0.1)
    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION
    assert exc_info.value.reason == "Not authenticated"


@pytest.mark.parametrize("url", ["/reports", "/tables", "/logout"])
@pytest.mark.asyncio(scope="session")
async def test_home_not_authenticated(anon_client: AsyncClient, url: str):
    resp = await anon_client.get(url)
    assert resp.is_redirect
    assert "/login" in resp.headers["Location"]


@pytest.mark.asyncio(scope="session")
async def test_login(anon_client: AsyncClient, auth_config: AuthSettings):
    data = {
        "username": auth_config.basic.username,
        "password": auth_config.basic.password,
    }
    resp = await anon_client.post("/auth/token", data=data)
    assert resp.is_success
    token_data = resp.json()
    assert "access_token" in token_data
    assert "access_token" in resp.cookies
    assert (
        f"Bearer {token_data['access_token']}" in resp.cookies["access_token"]
    )
    resp = await anon_client.post("/auth/revoke")
    assert resp.is_success


@pytest.mark.asyncio(scope="session")
async def test_logout(client: AsyncClient):
    resp = await client.post("/auth/revoke")
    assert resp.is_success
    assert "access_token" not in resp.cookies
    data = resp.json()
    assert {"message": "Выход из учетной записи!"} == data
