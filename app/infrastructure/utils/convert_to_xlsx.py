import asyncio
import logging
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired

logger = logging.getLogger(__name__)


async def convert_to_xlsx(path: Path, timeout: float | None = None) -> Path:
    cmd = [
        "libreoffice",
        "--convert-to",
        "xlsx",
        "--outdir",
        str(path.parent),
        str(path),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
    except asyncio.exceptions.TimeoutError:
        try:
            proc.kill()
        except OSError:
            # Игнорировать ошибку, например 'такой процесс отсутствует'
            pass
        raise TimeoutExpired(
            cmd,
            timeout,  # type: ignore[arg-type]
        )
    if stderr:
        raise CalledProcessError(
            proc.returncode,  # type: ignore[arg-type]
            cmd,
            stdout,
            stderr,
        )
    return path.with_suffix(".xlsx")
