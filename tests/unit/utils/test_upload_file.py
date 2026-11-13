import io

import pytest
from fastapi import UploadFile

from app.api.utils.upload_file import save_upload_file


@pytest.mark.asyncio
async def test_save_upload_file_strips_path(tmp_path):
    """filename с путём записывается как basename внутри base_dir."""
    base_dir = tmp_path / "uploads"
    base_dir.mkdir()
    file = UploadFile(io.BytesIO(b"data\n"), filename="../../evil.xlsm")

    saved = await save_upload_file(file, base_dir)

    assert saved == base_dir / "evil.xlsm"
    assert (base_dir / "evil.xlsm").exists()
    assert not (tmp_path / "evil.xlsm").exists()
