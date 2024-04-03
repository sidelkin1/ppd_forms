import logging
from typing import Any

import aioshutil
import anyio
from colorama import Fore

from app.api.dependencies.path import PathProvider

logger = logging.getLogger(__name__)


async def cron_clean_files(ctx: dict[str, Any]) -> None:
    path_provider: PathProvider = ctx["path_provider"]
    file_dir = anyio.Path(path_provider.file_dir)
    logger.info("Trying to clean %s%s", Fore.YELLOW, file_dir)
    async for child in file_dir.iterdir():
        if child.name == ".gitkeep":
            continue
        try:
            if await child.is_dir():
                await aioshutil.rmtree(child)
            else:
                await child.unlink()
        except Exception as error:
            logger.error(
                "%s%s%s deleting failed!",
                Fore.YELLOW,
                child,
                Fore.RESET,
                exc_info=error,
            )
    logger.info("%s%s%s was cleaned", Fore.YELLOW, file_dir, Fore.RESET)
