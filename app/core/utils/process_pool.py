import asyncio
import functools
from collections.abc import Callable
from concurrent.futures.process import ProcessPoolExecutor
from typing import ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


class ProcessPoolManager:
    def __init__(self, *, max_workers: int) -> None:
        self.pool = ProcessPoolExecutor(max_workers=max_workers)

    async def run(
        self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> T:
        if kwargs:
            func = functools.partial(func, **kwargs)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.pool, func, *args)

    def close(self) -> None:
        self.pool.shutdown()
