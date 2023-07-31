import asyncio
import functools
import typing
from concurrent.futures.process import ProcessPoolExecutor

from typing_extensions import ParamSpec

T = typing.TypeVar('T')
P = ParamSpec('P')


async def run_in_process(
    pool: ProcessPoolExecutor,
    func: typing.Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    if kwargs:
        func = functools.partial(func, **kwargs)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(pool, func, *args)
