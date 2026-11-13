from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status

COPY_BUFSIZE = 1024 * 1024


async def save_upload_file(file: UploadFile, base_dir: Path) -> Path:
    try:
        if file.filename is None:
            raise ValueError("filename must be set")
        # Берём только имя файла: filename из multipart-запроса может
        # содержать путь и вывести запись за пределы upload_dir.
        path = base_dir / Path(file.filename).name
        async with aiofiles.open(path, "wb") as f:
            while contents := await file.read(COPY_BUFSIZE):
                await f.write(contents)
        return path
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при загрузке файла!",
        ) from e
    finally:
        await file.close()
