import asyncio
import contextvars
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

import structlog
from structlog.contextvars import _ASYNC_CALLING_STACK


class BoundLogger(structlog.stdlib.BoundLogger):
    """
    TODO
    Меняем реализацию `BoundLogger._dispatch_to_sync`
    на версию из `AsyncBoundLogger._dispatch_to_sync`.
    Цель:
    - теперь можно использовать свою версию `executor`;
    - корректно сохраняются параметры места вызова (`callsite parameters`)
    """

    _executor = ThreadPoolExecutor(max_workers=8)

    async def _dispatch_to_sync(
        self,
        meth: Callable[..., Any],
        event: str,
        args: tuple[Any, ...],
        kw: dict[str, Any],
    ) -> None:
        """
        Merge contextvars and log using the sync logger in a thread pool.
        Callsite parameters are now also collected under asyncio.
        """
        scs_token = _ASYNC_CALLING_STACK.set(
            sys._getframe().f_back.f_back  # type: ignore
        )
        ctx = contextvars.copy_context()

        try:
            await asyncio.get_running_loop().run_in_executor(
                self._executor,
                lambda: ctx.run(lambda: meth(event, *args, **kw)),
            )
        finally:
            _ASYNC_CALLING_STACK.reset(scs_token)
