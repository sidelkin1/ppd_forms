import asyncio
from collections.abc import Callable

import pytest
from arq.worker import Function, Worker
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio(scope="session")
async def test_uneft_unknown_asset(client: AsyncClient):
    resp = await client.get("/uneft/unknown")
    assert not resp.is_success


@pytest.mark.asyncio(scope="session")
async def test_field_list_success(
    client: AsyncClient,
    worker: Callable[..., Worker],
    work_uneft: Function,
):
    worker_ = worker(functions=[work_uneft], burst=False)
    asyncio.create_task(worker_.main())
    resp = await client.get("/uneft/fields")
    assert resp.is_success
    data = resp.json()
    assert data == [{"id": 1, "name": "F1"}, {"id": 2, "name": "F2"}]


@pytest.mark.parametrize(
    "field_id,expected_data",
    [
        (1, [{"id": 1, "name": "R1"}, {"id": 2, "name": "R2"}]),
        (2, [{"id": 1, "name": "R1"}]),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_reservoir_list_success(
    client: AsyncClient,
    worker: Callable[..., Worker],
    work_uneft: Function,
    field_id: int,
    expected_data: list,
):
    worker_ = worker(functions=[work_uneft], burst=False)
    asyncio.create_task(worker_.main())
    resp = await client.get(f"/uneft/fields/{field_id}/reservoirs")
    assert resp.is_success
    data = resp.json()
    assert data == expected_data


@pytest.mark.asyncio(scope="session")
async def test_reservoir_list_unknown_field(
    client: AsyncClient,
    worker: Callable[..., Worker],
    work_uneft: Function,
):
    worker_ = worker(functions=[work_uneft], burst=False)
    asyncio.create_task(worker_.main())
    resp = await client.get("/uneft/fields/100/reservoirs")
    assert not resp.is_success
    assert resp.status_code == status.HTTP_404_NOT_FOUND
