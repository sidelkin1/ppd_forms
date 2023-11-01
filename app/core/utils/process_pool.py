import asyncio
import functools
from concurrent.futures.process import ProcessPoolExecutor
from typing import Callable, ParamSpec, TypeVar

from app.core.config.settings import Settings

T = TypeVar("T")
P = ParamSpec("P")


class ProcessPoolManager:
    def __init__(self, settings: Settings) -> None:
        self.pool = ProcessPoolExecutor(max_workers=settings.max_workers)

    async def run(
        self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> T:
        if kwargs:
            func = functools.partial(func, **kwargs)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.pool, func, *args)

    def close(self) -> None:
        self.pool.shutdown()
