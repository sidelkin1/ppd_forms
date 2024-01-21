from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status

COPY_BUFSIZE = 1024 * 1024


async def save_upload_file(file: UploadFile, base_dir: Path):
    try:
        if file.filename is None:
            raise ValueError("filename must be set")
        path = base_dir / file.filename
        path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(path, "wb") as f:
            while contents := await file.read(COPY_BUFSIZE):
                await f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при загрузке файла!",
        ) from e
    finally:
        await file.close()
