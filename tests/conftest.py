import asyncio

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for each test case.
    FIXME вроде бы проблема должна быть решена в pytest-asyncio >=0.23.3
    """
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
