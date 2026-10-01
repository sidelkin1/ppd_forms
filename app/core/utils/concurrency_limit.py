import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from weakref import WeakKeyDictionary

_limits: WeakKeyDictionary[
    asyncio.AbstractEventLoop, dict[str, asyncio.Semaphore]
] = WeakKeyDictionary()


@asynccontextmanager
async def concurrency_limit(
    name: str, limit: int
) -> AsyncGenerator[None, None]:
    """Ограничить число одновременно выполняющихся задач воркера.

    Лимит общий для всех задач одного имени в пределах процесса, поэтому
    семафор живёт в реестре, а не создаётся на каждый вызов. Реестр
    разделён по event loop: в Python 3.11+ ``asyncio.Semaphore``
    привязывается к первому использованному циклу, а воркер и тесты
    работают в разных. ``WeakKeyDictionary`` не удерживает мёртвые циклы.

    Потокобезопасность здесь не нужна: воркер однопоточный, все обращения
    идут из его event loop, а операции словаря под GIL атомарны.

    Размер семафора берётся при первом обращении к имени, последующие
    вызовы с другим ``limit`` этот размер не меняют.
    """
    loop = asyncio.get_running_loop()
    semaphores = _limits.setdefault(loop, {})
    if (sem := semaphores.get(name)) is None:
        sem = semaphores[name] = asyncio.Semaphore(limit)
    async with sem:
        yield
