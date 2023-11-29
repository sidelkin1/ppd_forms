import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.core.config.settings import settings

COPY_BUFSIZE = 1024 * 1024


async def save_upload_file(file: UploadFile):
    path = settings.base_dir / "excel" / file.filename
    try:
        async with aiofiles.open(path, "wb") as f:
            while contents := await file.read(COPY_BUFSIZE):
                await f.write(contents)
    except Exception:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при загрузке файла!",
        )  # TODO log
    finally:
        await file.close()
