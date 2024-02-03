from pathlib import Path

import pytest
from fastapi import UploadFile, status
from httpx import AsyncClient

from app.api.utils.upload_file import save_upload_file


@pytest.mark.asyncio(scope="session")
async def test_upload_file(
    client: AsyncClient, data_dir: Path, file_dir: Path
):
    files = {
        "file": ("test.csv", open(data_dir / "test.csv", "rb"), "text/plain")
    }
    resp = await client.post("excel/", files=files)
    assert resp.is_success
    data = resp.json()
    assert data == {"filename": "test.csv"}
    path = file_dir / "test_user" / "uploads" / "test.csv"
    assert path.exists()
    with open(path) as f:
        content = f.readlines()
    assert content == ["test"]


@pytest.mark.asyncio(scope="session")
async def test_download_report(
    client: AsyncClient, data_dir: Path, file_dir: Path
):
    file = UploadFile(open(data_dir / "test.csv", "rb"), filename="test.csv")
    await save_upload_file(file, file_dir / "test_user" / "results")
    resp = await client.get("reports/test")
    assert resp.is_success
    assert resp.content == b"test"


@pytest.mark.asyncio(scope="session")
async def test_download_unknown_report(client: AsyncClient):
    resp = await client.get("reports/unknown")
    assert not resp.is_success
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio(scope="session")
async def test_delete_report(
    client: AsyncClient, data_dir: Path, file_dir: Path
):
    file = UploadFile(open(data_dir / "test.csv", "rb"), filename="test.csv")
    await save_upload_file(file, file_dir / "test_user" / "results")
    resp = await client.delete("reports/test")
    assert resp.is_success
    assert not (file_dir / "test_user" / "results" / "test.csv").exists()


@pytest.mark.asyncio(scope="session")
async def test_delete_unknown_report(client: AsyncClient):
    resp = await client.delete("reports/unknown")
    assert not resp.is_success
    assert resp.status_code == status.HTTP_404_NOT_FOUND
